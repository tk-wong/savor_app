import { FlatList, Image, ImageSourcePropType, ListRenderItem, Platform, Text, TouchableOpacity, View } from "react-native";
import React, { useState } from "react";
import { SafeAreaView, useSafeAreaInsets } from "react-native-safe-area-context";
import { useHeaderHeight } from "@react-navigation/elements";
import { router } from "expo-router";

export default function AllRecipePage() {
    const headerHeight = useHeaderHeight();
    const insets = useSafeAreaInsets();
    const keyboardVerticalOffset = Platform.select({
        ios: headerHeight + insets.bottom,
        android: headerHeight, // Android often handles it better with just the header height
    });
    return <SafeAreaView style={{ paddingTop: keyboardVerticalOffset }}>
        <Text>All Recipes</Text>
        <RecipeCard />
        {Platform.OS === 'android' && <View style={{ height: insets.bottom }} />}
    </SafeAreaView>
}

interface Recipe {
    id: number;
    name: string;
    image: ImageSourcePropType;
}

function RecipeCard() {
    const [recipe_list, setRecipeList] = useState<Recipe[]>(Array.from({ length: 10 }, (_, i) => {
        return { name: `Recipe ${i}`, id: i, image: require("../../assets/images/react-logo.png") }
    }
    )
    );
    // TODO: fetch recipe list from backend and display it in a card format

    //  useEffect(() => {
    //      const list = Array.from({ length: 11 }, (_, i) => `Recipe ${i}`);
    //      setRecipeList(list);
    //  }, []);
    // const message = recipe_list.map((recipe) => {
    //     return <Text>{recipe}</Text>
    // })
    const renderItem: ListRenderItem<Recipe> = ({ item }) => {
        return <TouchableOpacity onPress={() => {
            // TODO: navigate to recipe detail page with the recipe id
            console.log(`Recipe id: ${item.id}`);
            router.push({ pathname: `/recipePage`, params: { id: item.id } })
        }
        }>
            <Image source={item.image} style={{ width: 100, height: 100 }} />
            <Text>{item.name}</Text>
        </TouchableOpacity>
    };
    return (

        <FlatList data={recipe_list} renderItem={renderItem} numColumns={2}
            keyExtractor={(item) => item.id.toString()} />

    )
}



