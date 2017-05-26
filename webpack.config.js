const path = require('path');
const webpack = require('webpack');

module.exports = {
  context: __dirname,
  entry: {
    databench: './js/src/index.ts',
  },
  output: {
    path: __dirname,
    library: 'Databench',
    libraryTarget: 'umd',
    filename: 'js/build/databench.js',
  },

  devtool: 'source-map',

  resolve: {
    extensions: ['', '.js', '.ts'],
    root: [
      path.join(__dirname, 'node_modules'),
      path.resolve('./js/src'),
    ],
  },

  plugins: [
    // new webpack.optimize.UglifyJsPlugin(),
  ],
  module: {
    preLoaders: [
      { test: /\.js$/, loader: 'source-map-loader' },
    ],
    loaders: [
      { test: /\.json$/, loader: 'json-loader' },
      { test: /\.tsx?$/, loader: 'ts-loader' },
      { test: /\.jsx?$/, loader: 'babel-loader', exclude: /node_modules/, query: ['es2015'] },
    ],
  },
}
