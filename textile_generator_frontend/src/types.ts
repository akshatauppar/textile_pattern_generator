export type StyleId = 'bandhani' | 'batik' | 'ikat' | 'block_print' | 'paisley';

export type BandhaniPattern = 'leheriya' | 'shikari' | 'mothra' | 'rajasthani_tie' | 'mandala';
export type BatikPattern = 'geometric_batik' | 'floral_batik' | 'traditional_batik' | 'wax_resist' | 'crackle';
export type IkatPattern = 'striped_ikat' | 'diamond_ikat' | 'blurred_motif' | 'traditional_ikat' | 'woven_pattern';
export type BlockPrintPattern = 'jaipuri_floral' | 'ajrakh_star' | 'buta_stamp' | 'geometric_lattice';
export type PaisleyPattern = 'royal_paisley' | 'floral_buta' | 'zardozi_swirl';

export type PatternId = BandhaniPattern | BatikPattern | IkatPattern | BlockPrintPattern | PaisleyPattern;

export interface StyleOption {
  id: StyleId;
  name: string;
  icon: string;
  description: string;
  patterns?: { id: PatternId; name: string; description: string }[];
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
  image_size?: number;
  reference_image?: string | null;
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
  reference_image?: string | null;
  fid_score?: number;
  model_checkpoint?: string;
  latency?: string;
}

export interface ApiHealth {
  status: string;
  model_loaded?: boolean;
  database?: string;
}

export interface BenchmarkData {
  project: {
    title: string;
  };
  specs: {
    architecture: string;
    checkpoint: string;
    dataset_size: number;
    dataset_classes: Record<string, number>;
    training_kimg: number;
    training_hardware: string;
    training_time: string;
    inference_latency_gpu: string;
    inference_latency_cpu: string;
    fid_score: number;
    resolution: string;
  };
  training_logs: {
    tick: number;
    progress: string;
    observation: string;
  }[];
  loss_curves: {
    early_phase: { kimg: number; d_loss: number; g_loss: number }[];
    full_run_trend: {
      initial_loss_range: string;
      divergence_point: string;
      peak_d_loss: string;
      moving_average_trend: string;
    };
  };
}
