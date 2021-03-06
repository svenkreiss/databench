module.exports = [

// for output to databench/static/databench.js
{
  context: __dirname,
  entry: {
    databench: './js/src/index.ts',
  },
  output: {
    path: __dirname,
    library: 'Databench',
    libraryTarget: 'umd',
    filename: 'databench/static/databench.js',
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
},

// for output to js/build/commonjs
{
  context: __dirname,
  entry: {
    databench: './js/src/index.ts',
  },
  output: {
    path: __dirname,
    library: 'Databench',
    libraryTarget: 'umd',
    filename: 'js/build/commonjs/databench.js',
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
}];
