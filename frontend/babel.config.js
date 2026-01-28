module.exports = function (api) {
    api.cache(true);
    const workletsPluginOptions = {}
    return {
        presets: ['babel-preset-expo'],
        plugins: ['react-native-worklets/plugin', workletsPluginOptions],
    };
};