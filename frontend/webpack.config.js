const path = require('path');

module.exports = {
    entry: {
        campaign: "./src/campaign/index.ts",
        handout: "./src/handout/index.ts",
        sheet: "./src/sheet/index.ts",
        coc: "./src/coc/index.ts"
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
        path: path.resolve(__dirname, '../app/static/js')
    }
};


