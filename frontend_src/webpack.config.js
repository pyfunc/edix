const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const MonacoWebpackPlugin = require('monaco-editor-webpack-plugin');

module.exports = (env, argv) => {
  const isProduction = argv.mode === 'production';
  
  return {
    entry: './src/index.js',
    output: {
      path: path.resolve(__dirname, '../edix/static'),
      filename: 'js/[name].[contenthash].js',
      publicPath: '/static/',
    },
    module: {
      rules: [
        {
          test: /\.(js|jsx)$/,
          exclude: /node_modules/,
          use: {
            loader: 'babel-loader',
          },
        },
        {
          test: /\.css$/,
          use: ['style-loader', 'css-loader'],
        },
        {
          test: /\.(png|svg|jpg|jpeg|gif|woff|woff2|eot|ttf|otf)$/i,
          type: 'asset/resource',
          generator: {
            filename: 'assets/[name].[hash][ext]',
          },
        },
      ],
    },
    resolve: {
      extensions: ['.js', '.jsx'],
      alias: {
        '@': path.resolve(__dirname, 'src/'),
      },
    },
    plugins: [
      new CleanWebpackPlugin({
        cleanOnceBeforeBuildPatterns: ['**/*', '!favicon.ico'],
      }),
      new HtmlWebpackPlugin({
        template: './public/index.html',
        filename: '../../edix/templates/editor.html',
        inject: 'body',
        publicPath: '/static/',
        minify: isProduction ? {
          collapseWhitespace: true,
          removeComments: true,
          removeRedundantAttributes: true,
          removeScriptTypeAttributes: true,
          removeStyleLinkTypeAttributes: true,
          useShortDoctype: true,
        } : false,
      }),
      new MonacoWebpackPlugin({
        languages: ['json', 'yaml', 'xml', 'html', 'javascript', 'typescript', 'python', 'sql', 'markdown'],
        features: [
          'accessibilityHelp',
          'bracketMatching',
          'caretOperations',
          'clipboard',
          'codeAction',
          'codelens',
          'colorDetector',
          'comment',
          'contextmenu',
          'coreCommands',
          'cursorUndo',
          'dnd',
          'find',
          'folding',
          'format',
          'gotoError',
          'gotoLine',
          'hover',
          'inPlaceReplace',
          'inspectTokens',
          'links',
          'linesOperations',
          'multicursor',
          'parameterHints',
          'quickCommand',
          'quickOutline',
          'referenceSearch',
          'rename',
          'smartSelect',
          'snippets',
          'suggest',
          'toggleHighContrast',
          'toggleTabFocusMode',
          'transpose',
          'wordHighlighter',
          'wordOperations',
          'wordPartOperations',
        ],
      }),
      new CopyWebpackPlugin({
        patterns: [
          {
            from: 'public',
            to: '.',
            globOptions: {
              ignore: ['**/index.html'],
            },
            noErrorOnMissing: true,
          },
        ],
      }),
    ],
    optimization: {
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
          },
        },
      },
      runtimeChunk: 'single',
    },
    devtool: isProduction ? 'source-map' : 'eval-source-map',
    devServer: {
      static: {
        directory: path.join(__dirname, '../edix/static'),
        publicPath: '/static/',
      },
      proxy: {
        '/api': 'http://localhost:8000',
        '/ws': {
          target: 'ws://localhost:8000',
          ws: true,
        },
      },
      hot: true,
      port: 3000,
      historyApiFallback: true,
      client: {
        overlay: {
          errors: true,
          warnings: false,
        },
      },
    },
  };
};
