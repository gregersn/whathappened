const path = require("path");
const { WebpackManifestPlugin } = require("webpack-manifest-plugin");
const options = {
    fileName: "manifest.json",
    publicPath: "/static/",
};

module.exports = {
    mode: "production",
    entry: {
        campaign: "./frontend/src/campaign/index.ts",
        handout: "./frontend/src/handout/index.ts",
        sheet: "./frontend/src/sheet/index.ts",
        coc7e: "./frontend/src/coc7e/index.ts",
        tftl: "./frontend/src/tftl/index.ts",
        tokens: "./frontend/src/tokens/index.ts",
        general: "./frontend/src/general/index.ts",
        system: "./frontend/src/system/index.ts",
    },
    module: {
        rules: [
            {
                test: /\.tsx?/,
                use: "ts-loader",
                exclude: "/node_modules/",
            },
        ],
    },
    resolve: {
        extensions: [".tsx", ".ts", ".js"],
    },
    output: {
        path: path.resolve(__dirname, "../src/whathappened/static/"),
        filename: "js/[name].[contenthash].js",
    },
    plugins: [new WebpackManifestPlugin(options)],
};
