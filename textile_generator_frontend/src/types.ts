export type StyleId = 'bandhani' | 'batik' | 'ikat';

export type BandhaniPattern = 'leheriya' | 'shikari' | 'mothra' | 'rajasthani_tie' | 'mandala';
export type BatikPattern = 'geometric_batik' | 'floral_batik' | 'traditional_batik' | 'wax_resist' | 'crackle';
export type IkatPattern = 'striped_ikat' | 'diamond_ikat' | 'blurred_motif' | 'traditional_ikat' | 'woven_pattern';

export type PatternId = BandhaniPattern | BatikPattern | IkatPattern;

export interface StyleOption {
  id: StyleId;
  name: string;
  icon: string;
  description: string;
}

export interface PatternOption {
  id: PatternId;
  name: string;
  description: string;
}

export interface GenerationRequest {
  prompt: string;
  style: StyleId;
  pattern?: PatternId;
  color_1?: string | null;
  color_2?: string | null;
  seed?: number | null;
  num_inference_steps?: number;
  guidance_scale?: number;
}

export interface GenerationStatus {
  id: number;
  status: 'processing' | 'completed' | 'failed';
  prompt: string;
  style: StyleId;
  pattern?: PatternId;
  color_1?: string | null;
  color_2?: string | null;
  seed?: number | null;
  image_url?: string | null;
  error_message?: string | null;
  created_at?: string;
  completed_at?: string | null;
  user_id?: number | null;
}

export interface ApiHealth {
  status: string;
  model_loaded?: boolean;
  database?: string;
}
