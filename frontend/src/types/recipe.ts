export interface DetailRecipe {
  id: number;
  name: string;
  ingredients: string[];
  instructions: string[];
  description: string;
  tips: string[];
  image_url?: string;
}

export interface Recipe {
  id: number;
  title: string;
  image_url?: string;
}