from flask import Blueprint, jsonify, request
from app.services.wikiSchema import WikiSchemaService

wikiSchema_blueprint = Blueprint('wikischema', __name__)


@wikiSchema_blueprint.route('/wikischema', methods=['POST'])
def add_wikiSchema():
  wikiSchema_data = request.json
  new_wikiSchema = WikiSchemaService.create_wikiSchema(wikiSchema_data)
  return jsonify(new_wikiSchema.to_dict()), 201


@wikiSchema_blueprint.route('/wikischema/<wikiSchema>', methods=['GET'])
def get_wikiSchema(wikiSchema):
  wikiSchema_obj = WikiSchemaService.get_one_wikiSchema(wikiSchema)
  if wikiSchema_obj:
    return jsonify(wikiSchema_obj.to_dict())
  return jsonify({'error': 'WikiSchema not found'}), 404


@wikiSchema_blueprint.route('/wikischema', methods=['GET'])
def get_wikiSchemas():
  wikiSchemas = WikiSchemaService.get_all_wikiSchemas()
  if wikiSchemas:
    return jsonify([wikiSchema.to_dict() for wikiSchema in wikiSchemas])
  return jsonify({'error': 'WikiSchemas not found'}), 404