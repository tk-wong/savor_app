import { router, useFocusEffect } from "expo-router";
import React, { useCallback, useMemo, useState } from "react";
import {
    Alert,
    FlatList,
    Image,
    ImageSourcePropType,
    ListRenderItem,
    StyleSheet,
    Text,
    TouchableOpacity,
    useWindowDimensions
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { ApiRequestError } from "../api/apiRequestError";
import { getAllRecipes } from "../api/recipe";
import { Recipe } from "../types";
import { StyledHeader } from "@/src/components/styledHeader";

const buildImageUrl = (base: string, imagePath?: string | null) => {
    if (!imagePath) {
        return undefined;
    }
    if (/^https?:\/\//i.test(imagePath)) {
        return imagePath;
    }

    const normalizedBase = String(base).replace(/\/+$/, "");
    let normalizedPath = String(imagePath).trim().replace(/\\/g, "/");
    if (normalizedBase.endsWith("/api") && normalizedPath.startsWith("/api/")) {
        normalizedPath = normalizedPath.slice(4);
    }
    if (!normalizedPath.startsWith("/")) {
        normalizedPath = `/${normalizedPath}`;
    }
    return `${normalizedBase}${normalizedPath}`;
};

export default function AllRecipePage() {
    return (<>
        <StyledHeader title={"All Recipes"} />
        <SafeAreaView className={"bg-surface flex-1"}>
            <RecipeCard />
        </SafeAreaView>
    </>)
}

interface RecipeCardItem {
    id: number;
    name: string;
    image: ImageSourcePropType;
}

function RecipeCard() {
    const [recipeList, setRecipeList] = useState<RecipeCardItem[]>([]);
    const { width } = useWindowDimensions();
    const numColumns = useMemo(() => {
        const idealItemWidth = 180; // most phones can fit 2 items at 180px, tablets can fit more
        const columns = Math.floor(width / idealItemWidth);
        return Math.min(4, Math.max(2, columns)); // force 2–4 columns range
    }, [width]);
    useFocusEffect(useCallback(() => {
        console.log("Fetching all recipes");
        const placeholderImage = "https://blocks.astratic.com/img/general-img-landscape.png";
        getAllRecipes().then((data) => {
            console.log(`Fetched recipe count: ${Array.isArray(data?.recipes) ? data.recipes.length : 0}`);
            const formattedRecipes = data.recipes.map((recipe: Recipe) => {
                const image_uri = buildImageUrl(process.env.EXPO_PUBLIC_BACKEND_URL ?? "", recipe.image_url) ?? placeholderImage;
                return {
                    id: recipe.id,
                    name: recipe.title,
                    image: { uri: image_uri },
                }
            });
            setRecipeList(formattedRecipes);
        }).catch((error: ApiRequestError) => {
            console.error("Error fetching recipes:", error.message);
            Alert.alert(`Error: ${error.status ?? "Unknown"}`, error.message ?? "Unknown error occurred while fetching all recipes.");
        })
    }, []));
    const renderItem: ListRenderItem<RecipeCardItem> = ({ item }) => {
        return <TouchableOpacity
            style={styles.card}
            onPress={() => {
                console.log(`Recipe id: ${item.id}`);
                router.push({ pathname: `/recipePage`, params: { id: item.id } })
            }
            }>
            <Image source={item.image} className={"max-w-full w-full aspect-square rounded-xl"} />
            <Text className={"mt-2 text-center text-sm global-text text-on-surface"}>{item.name}</Text>
        </TouchableOpacity>
    };
    return (
        <FlatList data={recipeList} renderItem={renderItem} numColumns={numColumns}
            key={numColumns}
            keyExtractor={(item, index) => `${item.id}-${index}`}
            contentContainerClassName={"gap-4 px-4 pb-6"}
            columnWrapperClassName={"gap-4"}
            className={"color-surface flex-1"}
        />
    )
}

const styles = StyleSheet.create({
    card: {
        flex: 1,
    },
});



