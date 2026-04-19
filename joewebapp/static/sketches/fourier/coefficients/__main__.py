from .country import country

print('Saving coefficients for Ukraine and Britain...')
country.save('ukraine', 'ukraine.geojson', 'coefficients.json')
country.save('britain', 'britain.geojson', 'coefficients.json')