"""'usuarios'

Revision ID: 482e682de4b8
Revises: 
Create Date: 2020-03-01 13:39:58.379513

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '482e682de4b8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default='1', nullable=False),
    sa.Column('username', sa.String(length=100, collation='NOCASE'), nullable=False),
    sa.Column('password', sa.String(length=255), server_default='', nullable=False),
    sa.Column('email_confirmed_at', sa.DateTime(), nullable=True),
    sa.Column('first_name', sa.String(length=100, collation='NOCASE'), nullable=False),
    sa.Column('last_name', sa.String(length=100, collation='NOCASE'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.add_column('despacho', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'despacho', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'despacho', type_='foreignkey')
    op.drop_column('despacho', 'user_id')
    op.drop_table('users')
    # ### end Alembic commands ###