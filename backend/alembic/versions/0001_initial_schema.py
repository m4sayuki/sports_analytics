"""initial backend schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-03-29 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '0001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


user_role = postgresql.ENUM('admin', 'coach', 'analyst', 'athlete', name='user_role', create_type=False)
team_member_role = postgresql.ENUM('owner', 'coach', 'manager', 'viewer', name='team_member_role', create_type=False)
video_status = postgresql.ENUM('uploaded', 'processing', 'ready', 'failed', name='video_status', create_type=False)
analysis_session_status = postgresql.ENUM('draft', 'in_progress', 'completed', 'archived', name='analysis_session_status', create_type=False)
point_source_type = postgresql.ENUM('manual', 'interpolated', 'auto_detected', name='point_source_type', create_type=False)
analysis_job_status = postgresql.ENUM('queued', 'running', 'succeeded', 'failed', name='analysis_job_status', create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    user_role.create(bind, checkfirst=True)
    team_member_role.create(bind, checkfirst=True)
    video_status.create(bind, checkfirst=True)
    analysis_session_status.create(bind, checkfirst=True)
    point_source_type.create(bind, checkfirst=True)
    analysis_job_status.create(bind, checkfirst=True)

    op.create_table('organizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('plan_type', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('slug', name='uq_organizations_slug'),
    )
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('email', sa.String(length=320), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('display_name', sa.String(length=255), nullable=False),
        sa.Column('role', user_role, nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_table('teams',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('sport_type', sa.String(length=100), nullable=False),
        sa.Column('season_label', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_teams_organization_id', 'teams', ['organization_id'], unique=False)
    op.create_table('team_members',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('membership_role', team_member_role, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('team_id', 'user_id', name='uq_team_members_team_user'),
    )
    op.create_index('ix_team_members_team_id', 'team_members', ['team_id'], unique=False)
    op.create_index('ix_team_members_user_id', 'team_members', ['user_id'], unique=False)
    op.create_table('athletes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('external_code', sa.String(length=100), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('kana_name', sa.String(length=255), nullable=True),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('sex', sa.String(length=30), nullable=True),
        sa.Column('dominant_side', sa.String(length=20), nullable=True),
        sa.Column('position_name', sa.String(length=100), nullable=True),
        sa.Column('height_cm', sa.Numeric(5, 2), nullable=True),
        sa.Column('weight_kg', sa.Numeric(5, 2), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_athletes_organization_id', 'athletes', ['organization_id'], unique=False)
    op.create_index('ix_athletes_team_id', 'athletes', ['team_id'], unique=False)
    op.create_table('videos',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('athlete_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('uploaded_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sport_type', sa.String(length=100), nullable=False),
        sa.Column('capture_date', sa.Date(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('camera_view', sa.String(length=50), nullable=True),
        sa.Column('frame_rate', sa.Numeric(8, 3), nullable=True),
        sa.Column('duration_ms', sa.BigInteger(), nullable=True),
        sa.Column('status', video_status, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['athlete_id'], ['athletes.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['uploaded_by_user_id'], ['users.id'], ondelete='RESTRICT'),
    )
    op.create_index('ix_videos_organization_id', 'videos', ['organization_id'], unique=False)
    op.create_index('ix_videos_team_id', 'videos', ['team_id'], unique=False)
    op.create_index('ix_videos_athlete_id', 'videos', ['athlete_id'], unique=False)
    op.create_index('ix_videos_uploaded_by_user_id', 'videos', ['uploaded_by_user_id'], unique=False)
    op.create_index('ix_videos_org_team_athlete', 'videos', ['organization_id', 'team_id', 'athlete_id'], unique=False)
    op.create_table('video_files',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('video_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('storage_provider', sa.String(length=50), nullable=False),
        sa.Column('bucket_name', sa.String(length=255), nullable=False),
        sa.Column('object_key', sa.String(length=1024), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=False),
        sa.Column('width_px', sa.Integer(), nullable=True),
        sa.Column('height_px', sa.Integer(), nullable=True),
        sa.Column('checksum_sha256', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_video_files_video_id', 'video_files', ['video_id'], unique=False)
    op.create_table('analysis_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('video_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('athlete_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_name', sa.String(length=255), nullable=False),
        sa.Column('analysis_type', sa.String(length=100), nullable=False),
        sa.Column('status', analysis_session_status, nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['athlete_id'], ['athletes.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='RESTRICT'),
    )
    op.create_index('ix_analysis_sessions_video_id', 'analysis_sessions', ['video_id'], unique=False)
    op.create_index('ix_analysis_sessions_athlete_id', 'analysis_sessions', ['athlete_id'], unique=False)
    op.create_index('ix_analysis_sessions_created_by_user_id', 'analysis_sessions', ['created_by_user_id'], unique=False)
    op.create_table('motion_tracks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('analysis_session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('body_part', sa.String(length=100), nullable=True),
        sa.Column('color_hex', sa.String(length=7), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_visible', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['analysis_session_id'], ['analysis_sessions.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_motion_tracks_analysis_session_id', 'motion_tracks', ['analysis_session_id'], unique=False)
    op.create_table('track_points',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('motion_track_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('frame_index', sa.Integer(), nullable=True),
        sa.Column('time_ms', sa.BigInteger(), nullable=False),
        sa.Column('x_norm', sa.Numeric(8, 6), nullable=False),
        sa.Column('y_norm', sa.Numeric(8, 6), nullable=False),
        sa.Column('confidence', sa.Numeric(5, 4), nullable=True),
        sa.Column('source_type', point_source_type, nullable=False),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint('x_norm >= 0 AND x_norm <= 1', name='ck_track_points_x_norm_range'),
        sa.CheckConstraint('y_norm >= 0 AND y_norm <= 1', name='ck_track_points_y_norm_range'),
        sa.ForeignKeyConstraint(['motion_track_id'], ['motion_tracks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_track_points_motion_track_id', 'track_points', ['motion_track_id'], unique=False)
    op.create_index('ix_track_points_created_by_user_id', 'track_points', ['created_by_user_id'], unique=False)
    op.create_index('ix_track_points_track_time', 'track_points', ['motion_track_id', 'time_ms'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_track_points_track_time', table_name='track_points')
    op.drop_index('ix_track_points_created_by_user_id', table_name='track_points')
    op.drop_index('ix_track_points_motion_track_id', table_name='track_points')
    op.drop_table('track_points')
    op.drop_index('ix_motion_tracks_analysis_session_id', table_name='motion_tracks')
    op.drop_table('motion_tracks')
    op.drop_index('ix_analysis_sessions_created_by_user_id', table_name='analysis_sessions')
    op.drop_index('ix_analysis_sessions_athlete_id', table_name='analysis_sessions')
    op.drop_index('ix_analysis_sessions_video_id', table_name='analysis_sessions')
    op.drop_table('analysis_sessions')
    op.drop_index('ix_video_files_video_id', table_name='video_files')
    op.drop_table('video_files')
    op.drop_index('ix_videos_org_team_athlete', table_name='videos')
    op.drop_index('ix_videos_uploaded_by_user_id', table_name='videos')
    op.drop_index('ix_videos_athlete_id', table_name='videos')
    op.drop_index('ix_videos_team_id', table_name='videos')
    op.drop_index('ix_videos_organization_id', table_name='videos')
    op.drop_table('videos')
    op.drop_index('ix_athletes_team_id', table_name='athletes')
    op.drop_index('ix_athletes_organization_id', table_name='athletes')
    op.drop_table('athletes')
    op.drop_index('ix_team_members_user_id', table_name='team_members')
    op.drop_index('ix_team_members_team_id', table_name='team_members')
    op.drop_table('team_members')
    op.drop_index('ix_teams_organization_id', table_name='teams')
    op.drop_table('teams')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
    op.drop_table('organizations')
    bind = op.get_bind()
    analysis_job_status.drop(bind, checkfirst=True)
    point_source_type.drop(bind, checkfirst=True)
    analysis_session_status.drop(bind, checkfirst=True)
    video_status.drop(bind, checkfirst=True)
    team_member_role.drop(bind, checkfirst=True)
    user_role.drop(bind, checkfirst=True)
