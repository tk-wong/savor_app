import { useHeaderHeight } from "@react-navigation/elements";
import { router, useFocusEffect } from "expo-router";
import React, { useCallback, useEffect, useState } from "react";
import { Alert, FlatList, Image, ImageSourcePropType, ListRenderItem, Platform, Text, TouchableOpacity, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { ApiRequestError } from "../api/apiRequestError";
import { getAllRecipes } from "../api/recipe";
import { Recipe } from "../types";

export default function AllRecipePage() {
    const headerHeight = useHeaderHeight();
    const insets = useSafeAreaInsets();
    // const keyboardVerticalOffset = Platform.select({
    //     ios: headerHeight + insets.bottom,
    //     android: headerHeight, // Android often handles it better with just the header height
    // });
    return <View>
        <RecipeCard />
        {Platform.OS === 'android' && <View style={{ height: insets.bottom }} />}
    </View>
}

interface RecipeCardItem {
    id: number;
    name: string;
    image: ImageSourcePropType;
}

function RecipeCard() {
    const [recipeList, setRecipeList] = useState<RecipeCardItem[]>([]);
    // TODO: fetch recipe list from backend and display it in a card format

    useFocusEffect(useCallback(() => {
        console.log("Fetching all recipes");
        getAllRecipes().then((data) => {
            const formattedRecipes = data.recipes.map((recipe: Recipe) => ({
                id: recipe.id,
                name: recipe.title,
                image: { uri: recipe.image_url }, // Convert image URL to ImageSourcePropType
            }));
            setRecipeList(formattedRecipes);
        }).catch((error: ApiRequestError) => {
            console.error("Error fetching recipes:", error.message);
            Alert.alert(`Error: ${error.status ?? "Unknown"}`, error.message ?? "Unknown error occurred while fetching all recipes.");
        })
    },[]));
    const renderItem: ListRenderItem<RecipeCardItem> = ({ item }) => {
        return <TouchableOpacity onPress={() => {
            console.log(`Recipe id: ${item.id}`);
            router.push({ pathname: `/recipePage`, params: { id: item.id } })
        }
        }>
            <Image source={item.image} style={{ width: 100, height: 100 }} />
            <Text>{item.name}</Text>
        </TouchableOpacity>
    };
    return (

        <FlatList data={recipeList} renderItem={renderItem} numColumns={2}
            keyExtractor={(item) => item.id.toString()} />

    )
}



