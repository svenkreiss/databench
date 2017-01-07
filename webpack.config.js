const path = require('path');

module.exports = {
  context: __dirname,
  entry: {
    databench: './js/src/main.ts'
  },
  output: {
    filename: './js/build/databench.js'
  },
  resolve: {
    extensions: ['', '.js', '.ts'],
    root: [
      path.join(__dirname, 'node_modules'),
      path.resolve('./js/src')
    ]
  },
  module: {
    loaders: [
      { test: /\.json$/, loader: "json-loader" },
      { test: /\.ts$/, loader: 'awesome-typescript-loader' }
    ],
		preLoaders: [
			{
				test: /\.js$/,
				// include: pathToRegExp(path.join(__dirname, "app")),
				loader: "jshint-loader"
			}
    ]
  }
}
