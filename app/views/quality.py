from flask import Blueprint, jsonify, request
from app.services.quality import QualityService

quality_blueprint = Blueprint('quality', __name__)


@quality_blueprint.route('/quality', methods=['POST'])
def add_quality():
  quality_data = request.json
  new_quality = QualityService.create_quality(quality_data)
  return jsonify(new_quality.to_dict()), 201


@quality_blueprint.route('/quality/<quality>', methods=['GET'])
def get_quality(quality):
  quality_obj = QualityService.get_one_quality(quality)
  if quality_obj:
    return jsonify(quality_obj.to_dict())
  return jsonify({'error': 'Quality not found'}), 404


@quality_blueprint.route('/quality', methods=['GET'])
def get_qualitys():
  qualities = QualityService.get_all_qualitys()
  if qualities:
    return jsonify([quality.to_dict() for quality in qualities])
  return jsonify({'error': 'Qualitys not found'}), 404


@quality_blueprint.route('/quality/gears', methods=['GET'])
def get_gear_qualities():
  qualities = QualityService.get_gear_qualities()
  if qualities:
    return jsonify([quality.to_dict() for quality in qualities])
  return jsonify({'error': 'Gear qualities not found'}), 404