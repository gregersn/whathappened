const path = require('path');
const { WebpackManifestPlugin } = require('webpack-manifest-plugin');
const options = {
    fileName: "manifest.json",
    stripSrc: true,
    publicPath: "/static/"
};

module.exports = {
    entry: {
        campaign: "./src/campaign/index.ts",
        handout: "./src/handout/index.ts",
        sheet: "./src/sheet/index.ts",
        coc7e: "./src/coc7e/index.ts"
    },
    module: {
        rules: [
            {
                test: /\.tsx?/,
                use: 'ts-loader',
                exclude: '/node_modules/'
            },
        ],
    },
    resolve: {
        extensions: ['.tsx', '.ts', '.js'],
    },
    output: {
        path: path.resolve(__dirname, '../app/static/'),
        filename: 'js/[name].[contenthash].js'
    },
    plugins: [
        new WebpackManifestPlugin(options)
    ]
};


