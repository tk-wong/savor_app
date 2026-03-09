module.exports = function (api) {
    api.cache(true);
    const workletsPluginOptions = {}
    return {
        presets: [
            ['babel-preset-expo', {jsxImportSource: "nativewind"}],
            "nativewind/babel"
        ],
        plugins: ['react-native-worklets/plugin', workletsPluginOptions],
    };
};