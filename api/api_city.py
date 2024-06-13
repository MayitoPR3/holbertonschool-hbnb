#!/usr/bin/python3
# API to manage cities


from flask import request
from flask_restx import fields, Namespace
from datamanagment import DataManager
from model.city import City



ns = Namespace('models', description='Model operations')

city_model = ns.model('City', {
    'id': fields.String(readOnly=True, description='The unique identifier of a city'),
    'name': fields.String(required=True, description='The name of the city'),
    'country_code': fields.String(required=True, description='The ISO country code of the city'),
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime
})


@ns.route('/')
class Cities(Resource):
    @ns.marshal_list_with(city_model)
    def get(self):
        """Fetch all cities."""
        return data_manager.get_all_cities()

    @ns.expect(city_model)
    @ns.response(201, 'City created successfully')
    @ns.response(400, 'Invalid request')
    @ns.response(409, 'City name already exists in the specified country')
    def post(self):
        """Create a new city."""
        new_city_data = request.json
        if not data_manager.get_country(new_city_data['country_id']):
            ns.abort(400, 'Invalid country ID')
        if any(city['name'] == new_city_data['name'] and city['country_id'] == new_city_data['country_id'] for city in data_manager.get_all_cities()):
            ns.abort(409, 'City name already exists in the specified country')
        new_city = City(new_city_data['name'], new_city_data['country_id'])
        data_manager.save_city(new_city.to_dict())
        return {'message': 'City created successfully', 'city_id': new_city.id}, 201

@ns.route('/<string:city_id>')
class CityResource(Resource):
    @ns.marshal_with(city_model)
    @ns.response(404, 'City not found')
    def get(self, city_id):
        """Fetch a city by its ID."""
        city = data_manager.get_city(city_id)
        if city:
            return city
        ns.abort(404, 'City not found')

    @ns.response(204, 'City deleted successfully')
    def delete(self, city_id):
        """Delete a city."""
        if data_manager.delete_city(city_id):
            return '', 204
        ns.abort(404, 'City not found')

    @ns.expect(city_model)
    @ns.response(204, 'City updated successfully')
    @ns.response(400, 'Invalid request')
    @ns.response(404, 'City not found')
    def put(self, city_id):
        """Update a city."""
        new_city_data = request.json
        new_city_data['city_id'] = city_id
        new_city_data['updated_at'] = datetime.now().isoformat()
        if data_manager.update_city(city_id, new_city_data):
            return '', 204
        ns.abort(404, 'City not found')
