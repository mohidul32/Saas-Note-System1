import os
import sys
import django
from pathlib import Path

# Add the project root to the path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import transaction
from faker import Faker
import random
from apps.companies.models import Company
from apps.workspaces.models import Workspace
from apps.users.models import User
from apps.notes.models import Note, Tag, Vote
from django.utils.text import slugify

fake = Faker()


def create_tags(count=100):
    """Create common tags"""
    print(f"Creating {count} tags...")
    tags = []
    tag_names = set()

    while len(tag_names) < count:
        tag_name = fake.word().lower()
        if tag_name not in tag_names:
            tag_names.add(tag_name)

    for tag_name in tag_names:
        tag, _ = Tag.objects.get_or_create(name=tag_name)
        tags.append(tag)

    print(f"Created {len(tags)} tags")
    return tags


def create_companies(count=50):
    """Create companies"""
    print(f"Creating {count} companies...")
    companies = []

    for i in range(count):
        company_name = fake.company()
        slug = slugify(company_name)

        # Ensure unique slug
        base_slug = slug
        counter = 1
        while Company.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        company = Company.objects.create(
            name=company_name,
            slug=slug,
            description=fake.catch_phrase(),
            is_active=True
        )
        companies.append(company)

        if (i + 1) % 10 == 0:
            print(f"  Created {i + 1} companies...")

    print(f"Created {len(companies)} companies")
    return companies


def create_users(companies, users_per_company=5):
    """Create users for each company"""
    print(f"Creating users ({users_per_company} per company)...")
    users = []

    for company in companies:
        # Create owner
        owner = User.objects.create_user(
            email=f"owner.{company.slug}@example.com",
            username=f"owner_{company.slug}",
            password="password123",
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            company=company,
            role='owner'
        )
        users.append(owner)

        # Create members
        for i in range(users_per_company - 1):
            member = User.objects.create_user(
                email=f"member{i}.{company.slug}@example.com",
                username=f"member{i}_{company.slug}",
                password="password123",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                company=company,
                role='member'
            )
            users.append(member)

    print(f"Created {len(users)} users")
    return users


def create_workspaces(companies, workspaces_per_company=20):
    """Create workspaces for each company"""
    print(f"Creating workspaces ({workspaces_per_company} per company)...")
    workspaces = []

    for company in companies:
        company_users = list(User.objects.filter(company=company))

        for i in range(workspaces_per_company):
            workspace_name = fake.bs().title()
            slug = slugify(workspace_name)

            # Ensure unique slug within company
            base_slug = slug
            counter = 1
            while Workspace.objects.filter(company=company, slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            workspace = Workspace.objects.create(
                name=workspace_name,
                slug=slug,
                description=fake.text(max_nb_chars=200),
                company=company,
                created_by=random.choice(company_users),
                is_active=True
            )
            workspaces.append(workspace)

    print(f"Created {len(workspaces)} workspaces")
    return workspaces


def create_notes(workspaces, tags, notes_per_workspace=500):
    """Create notes in workspaces"""
    print(f"Creating notes ({notes_per_workspace} per workspace)...")
    total_notes = len(workspaces) * notes_per_workspace
    created = 0
    batch_size = 1000
    notes_batch = []

    for workspace in workspaces:
        company_users = list(User.objects.filter(company=workspace.company))

        for i in range(notes_per_workspace):
            note = Note(
                title=fake.sentence(nb_words=6),
                content=fake.text(max_nb_chars=1000),
                note_type=random.choice(['public', 'public', 'private']),  # More public notes
                is_draft=random.choice([True, False]) if random.random() < 0.2 else False,
                workspace=workspace,
                created_by=random.choice(company_users),
                updated_by=random.choice(company_users)
            )
            notes_batch.append(note)

            if len(notes_batch) >= batch_size:
                Note.objects.bulk_create(notes_batch)
                created += len(notes_batch)
                notes_batch = []
                print(f"  Created {created}/{total_notes} notes...")

    # Create remaining notes
    if notes_batch:
        Note.objects.bulk_create(notes_batch)
        created += len(notes_batch)

    print(f"Created {created} notes")

    # Add tags to notes
    print("Adding tags to notes...")
    all_notes = Note.objects.all()
    for i, note in enumerate(all_notes):
        num_tags = random.randint(1, 5)
        note.tags.set(random.sample(tags, num_tags))

        if (i + 1) % 10000 == 0:
            print(f"  Tagged {i + 1} notes...")

    print(f"Tagged all notes")
    return list(all_notes)


def create_votes(notes, companies):
    """Create votes for public notes"""
    print("Creating votes for public notes...")
    public_notes = [n for n in notes if n.note_type == 'public' and not n.is_draft]

    # Sample notes to vote on (not all)
    notes_to_vote = random.sample(public_notes, min(len(public_notes), 100000))

    votes_batch = []
    batch_size = 1000
    created = 0

    for note in notes_to_vote:
        # Random number of votes per note
        num_votes = random.randint(0, 20)

        for _ in range(num_votes):
            vote_type = random.choice(['upvote', 'upvote', 'downvote'])  # More upvotes
            voting_company = random.choice(companies)

            # Check if this company already voted
            if not Vote.objects.filter(note=note, company=voting_company).exists():
                vote = Vote(
                    note=note,
                    company=voting_company,
                    vote_type=vote_type
                )
                votes_batch.append(vote)

                if len(votes_batch) >= batch_size:
                    Vote.objects.bulk_create(votes_batch, ignore_conflicts=True)
                    created += len(votes_batch)
                    votes_batch = []
                    print(f"  Created {created} votes...")

    # Create remaining votes
    if votes_batch:
        Vote.objects.bulk_create(votes_batch, ignore_conflicts=True)
        created += len(votes_batch)

    print(f"Created {created} votes")


def seed_database():
    """Main seeding function"""
    print("=" * 60)
    print("STARTING DATABASE SEEDING")
    print("=" * 60)

    try:
        with transaction.atomic():
            # Create data
            tags = create_tags(count=100)
            companies = create_companies(count=50)
            users = create_users(companies, users_per_company=5)
            workspaces = create_workspaces(companies, workspaces_per_company=20)
            notes = create_notes(workspaces, tags, notes_per_workspace=500)
            create_votes(notes, companies)

            print("=" * 60)
            print("DATABASE SEEDING COMPLETED SUCCESSFULLY")
            print("=" * 60)
            print(f"Summary:")
            print(f"  - Companies: {len(companies)}")
            print(f"  - Users: {len(users)}")
            print(f"  - Workspaces: {len(workspaces)}")
            print(f"  - Notes: {len(notes)}")
            print(f"  - Tags: {len(tags)}")
            print("=" * 60)

    except Exception as e:
        print(f"ERROR: {str(e)}")
        raise


if __name__ == '__main__':
    seed_database()