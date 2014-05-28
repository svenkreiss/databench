from flask import Blueprint, render_template

listAll = []

class Analysis:
	def __init__(self, name, importName, signals, description=None, blueprint=None):
		"""
		An optional flask blueprint can be dependency-injected.
		"""

		listAll.append(self)
		self.name = name
		self.importName = importName
		self.signals = signals
		self.description = description

		if not blueprint:
			self.blueprint = Blueprint(
				name, 
				importName,
				template_folder='templates'
			)
		else:
			self.blueprint = blueprint

		@self.blueprint.route('/')
		def render_index():
			return render_template(self.name+'.html')
