from flask import request, jsonify
from models import db, Tournament, Team


def get_tournaments():
    tournaments = Tournament.query.all()
    tournament_data = [{
        'id': tournament.id,
        'title': tournament.title,
        'location': tournament.location,
        'start_time': tournament.start_time.isoformat(),
        'end_time': tournament.end_time.isoformat(),
        'discipline': tournament.discipline,
        'prize_pool': tournament.prize_pool,
        'image_url': tournament.image_url,
        'description': tournament.description  # Include the description in the response
    } for tournament in tournaments]
    return jsonify(tournaments=tournament_data)


def add_tournament():
    data = request.get_json()
    required_fields = ['title', 'location', 'start_time', 'end_time', 'discipline', 'prize_pool',
                       'description']  # Добавляем 'description' в список обязательных полей
    if not all(field in data for field in required_fields):
        return jsonify(error="All required fields must be provided"), 400
    new_tournament = Tournament(**data)
    db.session.add(new_tournament)
    db.session.commit()
    return jsonify(message="Tournament added", tournament_id=new_tournament.id), 201


def add_register_team():
    data = request.get_json(force=True)
    required_fields = ["team_name", "representative_name", "representative_email", "members", "tournament_name",
                       "discipline"]
    if not all(data.get(field) for field in required_fields):
        return jsonify({'error': 'Missing data'}), 400

    new_team = Team(
        team_name=data['team_name'],
        representative_name=data['representative_name'],
        representative_email=data['representative_email'],
        members=data['members'],
        tournament_name=data['tournament_name'],
        discipline=data['discipline']
    )
    db.session.add(new_team)
    db.session.commit()
    return jsonify(message="Team registered successfully", team_id=new_team.id), 201


def get_teams():
    teams = Team.query.all()
    team_data = [{
        'id': team.id,
        'team_name': team.team_name,
        'representative_name': team.representative_name,
        'representative_email': team.representative_email,
        'members': team.members,
        'tournament_name': team.tournament_name,
        'discipline': team.discipline
    } for team in teams]
    return jsonify(teams=team_data)
