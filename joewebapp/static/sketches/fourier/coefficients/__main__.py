from .country import country
from .svg import svg

print('Saving coefficients for Ukraine and Britain...')
country.save('ukraine', 'ukraine.geojson', 'coefficients.json')
country.save('britain', 'britain.geojson', 'coefficients.json')

print('Saving coefficients for SVGs...')
svg.save()