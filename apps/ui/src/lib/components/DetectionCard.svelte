<script lang="ts">
    import type { Detection } from '../api';
    
    interface Props {
        detection: Detection;
    }

    let { detection }: Props = $props();
</script>

<div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-200">
    <div class="relative h-48 bg-gray-200 dark:bg-gray-700">
        <!-- Placeholder for image, assuming typical Frigate URL structure if we had one, or just a placeholder -->
        <div class="absolute inset-0 flex items-center justify-center text-gray-400">
            <span class="text-4xl">🐦</span>
        </div>
        <!-- In a real app we'd construct the image URL -->
        <!-- <img src="..." alt={detection.display_name} class="w-full h-full object-cover" /> -->
        
        <div class="absolute top-2 right-2 bg-black bg-opacity-50 text-white text-xs px-2 py-1 rounded">
            {(detection.score * 100).toFixed(0)}%
        </div>
    </div>
    <div class="p-4">
        <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-1 truncate" title={detection.display_name}>
            {detection.display_name}
        </h3>
        <div class="flex justify-between items-center text-sm text-gray-500 dark:text-gray-400">
            <span>{detection.camera_name}</span>
            <span>{new Date(detection.detection_time).toLocaleTimeString()}</span>
        </div>
        <div class="mt-2 text-xs text-gray-400">
            {new Date(detection.detection_time).toLocaleDateString()}
        </div>
    </div>
</div>
