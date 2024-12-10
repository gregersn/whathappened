const { merge } = require("webpack-merge");

const common = require("./webpack.common.js");

module.exports = merge(common, {
    mode: "development",
    devtool: "inline-source-map",
    output: {
        devtoolModuleFilenameTemplate: "file:///[absolute-resource-path]", // map to source with absolute file path not webpack:// protocol
    },
});
