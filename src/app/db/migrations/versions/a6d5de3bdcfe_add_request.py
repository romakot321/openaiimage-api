"""add request

Revision ID: a6d5de3bdcfe
Revises: d5347431df83
Create Date: 2025-05-01 11:49:14.002885

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a6d5de3bdcfe'
down_revision = 'd5347431df83'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('task_requests',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('task_id', sa.Uuid(), nullable=False),
    sa.Column('schema', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("(now() at time zone 'utc')"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_task_requests_id'), 'task_requests', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_task_requests_id'), table_name='task_requests')
    op.drop_table('task_requests')
    # ### end Alembic commands ###
