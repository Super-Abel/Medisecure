const { merge } = require("webpack-merge");
const commonConfig = require("./common.config");

module.exports = merge(commonConfig, {
  mode: "development",
  devtool: "inline-source-map",
  output: {
    publicPath: "/static/webpack_bundles/",
  },
});
