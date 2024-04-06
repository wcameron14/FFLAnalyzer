from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db


class User(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    email_confirmed = db.Column(db.Boolean, default=False)
    confirmed_at = db.Column(db.DateTime)
    confirmation_sent_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=False)
    sleeper_id = db.Column(db.String(64), unique=True, nullable=True)
    is_logged_in = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.id)
    
    @property
    def is_authenticated(self):
        return self.is_logged_in
    
class SleeperID(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String)
    display_name = db.Column(db.String)
    avatar = db.Column(db.String)

class Leagues(db.Model):
    league_id = db.Column(db.String, primary_key=True)
    name = db.Column(db.Text)
    season = db.Column(db.Integer)
    status = db.Column(db.Text)
    sport = db.Column(db.Text)
    total_rosters = db.Column(db.Integer)
    previous_league_id = db.Column(db.Text)
    draft_id = db.Column(db.Text)
    avatar = db.Column(db.String)

class Players(db.Model):
    player_id = db.Column(db.String, primary_key=True)
    full_name = db.Column(db.String)
    position = db.Column(db.String)
    team = db.Column(db.String)
    age = db.Column(db.Integer)
    years_exp = db.Column(db.Integer)
    name_xref = db.Column(db.String)
    gamedata_id = db.Column(db.String)

class LeagueOwners(db.Model):
    league_id = db.Column(db.String)
    display_name = db.Column(db.String)
    user_id = db.Column(db.String)
    is_owner = db.Column(db.Boolean)
    __table_args__ = (
        db.PrimaryKeyConstraint('league_id', 'user_id'),
    )

class TeamName(db.Model):
    user_id = db.Column(db.String, primary_key=True)
    display_name = db.Column(db.String)
    league_id = db.Column(db.String)
    team_name = db.Column(db.String)

class Rosters(db.Model):
    league_id = db.Column(db.String)
    owner_id = db.Column(db.String)
    roster_id = db.Column(db.String)
    players = db.Column(db.String)
    reserve = db.Column(db.String)
    starters = db.Column(db.String)
    wins = db.Column(db.Integer)
    waiver_position = db.Column(db.Integer)
    waiver_budget_used = db.Column(db.Integer)
    total_moves = db.Column(db.Integer)
    ties = db.Column(db.Integer)
    losses = db.Column(db.Integer)
    fpts_decimal = db.Column(db.Integer)
    fpts_against_decimal = db.Column(db.Integer)
    fpts_against = db.Column(db.Integer)
    fpts = db.Column(db.Integer)
    __table_args__ = (
        db.PrimaryKeyConstraint('league_id', 'owner_id'),
    )

class Matchups(db.Model):
    league_id = db.Column(db.String)
    roster_id = db.Column(db.String)
    matchup_id = db.Column(db.String)
    starters = db.Column(db.String)
    players = db.Column(db.String)
    points = db.Column(db.Float)
    custom_points = db.Column(db.Float)
    __table_args__ = (
        db.PrimaryKeyConstraint('league_id', 'roster_id', 'matchup_id'),
    )
    
class Trades(db.Model):
    transaction_id = db.Column(db.String)
    league_id = db.Column(db.String)
    type = db.Column(db.String)
    status = db.Column(db.String)
    roster_ids = db.Column(db.String)
    creator = db.Column(db.String)
    week = db.Column(db.Integer)
    consenter_ids = db.Column(db.String)
    drops = db.Column(db.JSON)
    adds = db.Column(db.JSON)
    __table_args__ = (
        db.PrimaryKeyConstraint('transaction_id', 'league_id'),
    )

class Waivers(db.Model):
    transaction_id = db.Column(db.String)
    league_id = db.Column(db.String)
    type = db.Column(db.String)
    status = db.Column(db.String)
    roster_ids = db.Column(db.String)
    drops = db.Column(db.JSON)
    adds = db.Column(db.JSON)
    creator = db.Column(db.String)
    created = db.Column(db.String)
    week = db.Column(db.Integer)
    consenter_ids = db.Column(db.String)
    settings = db.Column(db.JSON)
    __table_args__ = (
    db.PrimaryKeyConstraint('transaction_id', 'league_id'),
)

class TradedDraftPicks(db.Model):
    transaction_id = db.Column(db.String)
    season = db.Column(db.Integer)
    round = db.Column(db.Integer)
    roster_id = db.Column(db.Integer)
    previous_owner_id = db.Column(db.Integer)
    league_id = db.Column(db.String)
    owner_id = db.Column(db.Integer)
    __table_args__ = (
        db.PrimaryKeyConstraint('transaction_id', 'season', 'round', 'roster_id', 'previous_owner_id'),
    )

class TradedWaiverBudget(db.Model):
    league_id = db.Column(db.String)
    transaction_id = db.Column(db.String, primary_key=True)
    sender = db.Column(db.Integer)
    receiver = db.Column(db.Integer)
    amount = db.Column(db.Integer)

class LeagueSettings(db.Model):
    league_id = db.Column(db.String, primary_key=True)
    total_rosters = db.Column(db.Integer)
    status = db.Column(db.Text)
    sport = db.Column(db.Text)
    settings = db.Column(db.JSON)
    season_type = db.Column(db.Text)
    season = db.Column(db.Text)
    scoring_settings = db.Column(db.JSON)
    roster_positions = db.Column(db.JSON)
    previous_league_id = db.Column(db.Text)
    name = db.Column(db.Text)
    draft_id = db.Column(db.Text)
    avatar = db.Column(db.Text)

class DraftPicks(db.Model):
    player_id = db.Column(db.String)
    picked_by = db.Column(db.String)
    roster_id = db.Column(db.Text)
    round = db.Column(db.String)
    draft_slot = db.Column(db.String)
    pick_no = db.Column(db.String)
    amount = db.Column(db.Integer)
    team = db.Column(db.Text)
    status = db.Column(db.Text)
    sport = db.Column(db.Text)
    position = db.Column(db.Text)
    number = db.Column(db.String)
    news_updated = db.Column(db.String)
    last_name = db.Column(db.Text)
    injury_status = db.Column(db.Text)
    first_name = db.Column(db.Text)
    is_keeper = db.Column(db.Boolean)
    draft_id = db.Column(db.Text)
    __table_args__ = (
        db.PrimaryKeyConstraint('player_id', 'draft_id'),
    )

class TA_LeagueSettings(db.Model):
    __tablename__ = 'ta_league_settings'
    league_id = db.Column(db.String, primary_key=True)
    pass_yd = db.Column(db.Integer)
    pass_td = db.Column(db.Integer)
    pass_2pt = db.Column(db.Integer)
    pass_int = db.Column(db.Integer)
    fum = db.Column(db.Integer)
    fum_lost = db.Column(db.Integer)
    rush_yd = db.Column(db.Integer)
    rush_td = db.Column(db.Integer)
    rush_2pt = db.Column(db.Integer)
    rec = db.Column(db.Integer)
    rec_yd = db.Column(db.Integer)
    rec_td = db.Column(db.Integer)
    rec_2pt = db.Column(db.Integer)
    pts_allow_0 = db.Column(db.Integer)
    pts_allow_1_6 = db.Column(db.Integer)
    pts_allow_7_13 = db.Column(db.Integer)
    pts_allow_14_20 = db.Column(db.Integer)
    pts_allow_21_27 = db.Column(db.Integer)
    pts_allow_28_34 = db.Column(db.Integer)
    pts_allow_35p = db.Column(db.Integer)
    sack = db.Column(db.Integer)
    int = db.Column(db.Integer)
    safe = db.Column(db.Integer)
    def_td = db.Column(db.Integer)
    st_td = db.Column(db.Integer)
    def_st_td = db.Column(db.Integer)
    ff = db.Column(db.Integer)
    st_ff = db.Column(db.Integer)
    def_st_ff = db.Column(db.Integer)
    fum_rec = db.Column(db.Integer)
    def_st_fum_rec = db.Column(db.Integer)
    st_fum_rec = db.Column(db.Integer)
    blk_kick = db.Column(db.Integer)
    xpm = db.Column(db.Integer)
    xpmiss = db.Column(db.Integer)
    fgm_0_19 = db.Column(db.Integer)
    fgm_20_29 = db.Column(db.Integer)
    fgm_30_39 = db.Column(db.Integer)
    fgm_40_49 = db.Column(db.Integer)
    fgm_50p = db.Column(db.Integer)
    fgmiss = db.Column(db.Integer)
    fgmiss_0_19 = db.Column(db.Integer)
    fgmiss_20_29 = db.Column(db.Integer)
    fgmiss_30_39 = db.Column(db.Integer)
    fgmiss_40_49 = db.Column(db.Integer)







