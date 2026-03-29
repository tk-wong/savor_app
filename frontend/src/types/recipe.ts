export interface DetailRecipe {
  id: number;
  title: string;
  ingredients: Ingredient[];
  directions: string[];
  description: string;
  tips: string[];
  image_url?: string;
}

export interface Recipe {
  id: number;
  title: string;
  image_url?: string;
}

export interface Ingredient {
  ingredient_name: string;
  quantity: string;
}