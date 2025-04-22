"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade():
    ${upgrades if upgrades else "pass"}
    
    # Manually add code to drop document_folders table if it exists
    op.execute("""
    DROP TABLE IF EXISTS document_folders CASCADE;
    """)
    
    # Ensure documents table has folder_id foreign key
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'documents' AND column_name = 'folder_id'
        ) THEN
            ALTER TABLE documents ADD COLUMN folder_id INTEGER REFERENCES folders(id);
        END IF;
    END
    $$;
    """)


def downgrade():
    ${downgrades if downgrades else "pass"}
