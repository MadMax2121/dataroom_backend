"""simplified data tables

Revision ID: 7bf4db0c66d9
Revises: a4aec6f5eda4
Create Date: 2025-04-08 20:16:53.012127

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7bf4db0c66d9'
down_revision = 'a4aec6f5eda4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('document_folders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('folder_id', sa.Integer(), nullable=False),
    sa.Column('document_id', sa.Integer(), nullable=False),
    sa.Column('added_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
    sa.ForeignKeyConstraint(['folder_id'], ['folders.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('folder_id', 'document_id', name='uix_document_folder')
    )
    op.drop_table('folder_documents')
    op.drop_table('folder_permissions')
    op.drop_table('document_tags')
    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tags', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.drop_column('tags')

    op.create_table('document_tags',
    sa.Column('document_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], name='document_tags_document_id_fkey'),
    sa.PrimaryKeyConstraint('document_id', 'name', name='document_tags_pkey')
    )
    op.create_table('folder_permissions',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('folder_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('permission_type', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['folder_id'], ['folders.id'], name='folder_permissions_folder_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='folder_permissions_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='folder_permissions_pkey')
    )
    op.create_table('folder_documents',
    sa.Column('folder_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('document_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('added_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], name='folder_documents_document_id_fkey'),
    sa.ForeignKeyConstraint(['folder_id'], ['folders.id'], name='folder_documents_folder_id_fkey'),
    sa.PrimaryKeyConstraint('folder_id', 'document_id', name='folder_documents_pkey')
    )
    op.drop_table('document_folders')
    # ### end Alembic commands ###
