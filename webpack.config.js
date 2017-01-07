module.exports = {
  entry: {
    databench: './js/src/main.ts'
  },
  output: {
    filename: './js/build/databench.js'
  },
  module: {
    loaders: [
      {
        test: /\.ts$/,
        loader: 'awesome-typescript-loader'
      }
    ]
  }
}
