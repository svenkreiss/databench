const path = require('path');
const webpack = require('webpack');

module.exports = {
  context: __dirname,
  entry: {
    databench: './js/src/index.ts',
  },
  output: {
    path: __dirname,
    filename: 'js/build/databench.js',
  },

  devtool: 'source-map',

  resolve: {
    extensions: ['.ts', '.tsx', '.js', '.json'],
  },

  module: {
    rules: [
      { test: /\.jsx?$/, loader: 'babel-loader' },
      { test: /\.tsx?$/, loader: 'awesome-typescript-loader' },
      { enforce: 'pre', test: /\.js$/, loader: 'source-map-loader' }
    ]
  },
}
