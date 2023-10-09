const path = require("path");
const { WebpackManifestPlugin } = require("webpack-manifest-plugin");
const options = {
    fileName: "manifest.json",
    publicPath: "/static/",
};

module.exports = {
    mode: "production",
    entry: {
        campaign: "./src/campaign/index.ts",
        handout: "./src/handout/index.ts",
        sheet: "./src/sheet/index.ts",
        coc7e: "./src/coc7e/index.ts",
        tftl: "./src/tftl/index.ts",
        tokens: "./src/tokens/index.ts",
        general: "./src/general/index.ts",
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
        devtoolModuleFilenameTemplate: "file:///[absolute-resource-path]", // map to source with absolute file path not webpack:// protocol
    },
    plugins: [new WebpackManifestPlugin(options)],
    devtool: "inline-source-map",
};
