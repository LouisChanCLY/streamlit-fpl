from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional, Any


class Label(BaseModel):
    label: str
    name: str


class Position(BaseModel):
    id: int
    plural_name: str
    singular_name: str
    squad_select: int
    squad_min_play: int
    squad_max_play: int
    ui_shirt_specific: bool
    element_count: int


class PositionList(BaseModel):
    positions: List[Position]

    @property
    def singular_names(self) -> List[str]:
        return [position.singular_name for position in self.positions]

    @property
    def plural_names(self) -> List[str]:
        return [position.plural_name for position in self.positions]


class Fixture(BaseModel):
    id: int
    event: int
    team_a: int
    team_a_difficulty: int
    team_h: int
    team_h_difficulty: int
    kickoff_time: str
    finished: bool


class Player(BaseModel):
    assists: int
    bonus: int
    bps: int
    chance_of_playing_next_round: Optional[float]
    chance_of_playing_this_round: Optional[float]
    clean_sheets: int
    clean_sheets_per_90: float
    code: int
    corners_and_indirect_freekicks_order: Optional[float]
    corners_and_indirect_freekicks_text: str
    cost_change_event: int
    cost_change_event_fall: int
    cost_change_start: int
    cost_change_start_fall: int
    creativity: float
    creativity_rank: int
    creativity_rank_type: int
    direct_freekicks_order: Optional[float]
    direct_freekicks_text: str
    dreamteam_count: int
    element_type: int
    ep_next: float
    ep_this: Optional[float]
    event_points: int
    expected_assists: float
    expected_assists_per_90: float
    expected_goal_involvements: float
    expected_goal_involvements_per_90: float
    expected_goals: float
    expected_goals_conceded: float
    expected_goals_conceded_per_90: float
    expected_goals_per_90: float
    first_name: str
    form: float
    form_rank: int
    form_rank_type: int
    goals_conceded: int
    goals_conceded_per_90: float
    goals_scored: int
    ict_index: float
    ict_index_rank: int
    ict_index_rank_type: int
    id: int
    in_dreamteam: bool
    influence: float
    influence_rank: int
    influence_rank_type: int
    minutes: int
    news: str
    news_added: Optional[Any]
    now_cost: int
    now_cost_rank: int
    now_cost_rank_type: int
    own_goals: int
    penalties_missed: int
    penalties_order: Optional[float]
    penalties_saved: int
    penalties_text: str
    photo: str
    points_per_game: float
    points_per_game_rank: int
    points_per_game_rank_type: int
    red_cards: int
    saves: int
    saves_per_90: float
    second_name: str
    selected_by_percent: float
    selected_rank: int
    selected_rank_type: int
    special: bool
    squad_number: Optional[int]
    starts: int
    starts_per_90: float
    status: str
    team: int
    team_code: int
    threat: float
    threat_rank: int
    threat_rank_type: int
    total_points: int
    transfers_in: int
    transfers_in_event: int
    transfers_out: int
    transfers_out_event: int
    value_form: float
    value_season: float
    web_name: str
    yellow_cards: int


class Event(BaseModel):
    average_entry_score: float
    chip_plays: List[Any]
    cup_leagues_created: bool
    data_checked: bool
    deadline_time: datetime
    deadline_time_epoch: int
    deadline_time_game_offset: int
    finished: bool
    h2h_ko_matches_created: bool
    highest_score: Optional[float]
    highest_scoring_entry: Optional[Any]
    id: int
    is_current: bool
    is_next: bool
    is_previous: bool
    most_captained: Optional[Any]
    most_selected: Optional[Any]
    most_transferred_in: Optional[Any]
    most_vice_captained: Optional[Any]
    name: str
    ranked_count: int
    release_time: Optional[datetime]
    top_element: Optional[Any]
    top_element_info: Optional[Any]
    transfers_made: int


class Team(BaseModel):
    code: int
    draw: int
    form: Optional[Any]
    id: int
    loss: int
    name: str
    played: int
    points: int
    position: int
    short_name: str
    strength: int
    team_division: Optional[Any]
    unavailable: bool
    win: int
    strength_overall_home: int
    strength_overall_away: int
    strength_attack_home: int
    strength_attack_away: int
    strength_defence_home: int
    strength_defence_away: int
    pulse_id: int
