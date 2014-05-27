from flask import Blueprint, render_template

myanalysis = Blueprint(
	'myanalysis', 
	__name__,
	template_folder='templates'
)

@myanalysis.route('/')
def index():
	return render_template('overview.html')
