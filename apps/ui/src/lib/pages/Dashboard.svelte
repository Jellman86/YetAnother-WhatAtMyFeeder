<script lang="ts">
    import DetectionCard from '../components/DetectionCard.svelte';
    import type { Detection } from '../api';

    let { detections } = $props<{ detections: Detection[] }>();
</script>

<div class="mb-8">
    <h2 class="text-2xl font-bold mb-4 text-gray-900 dark:text-white">Live Detections</h2>
</div>

<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
    {#each detections as detection (detection.frigate_event || detection.id)}
        <DetectionCard {detection} />
    {/each}
    
    {#if detections.length === 0}
        <div class="col-span-full text-center py-12 text-gray-500 dark:text-gray-400 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700">
            <div class="flex flex-col items-center justify-center">
                 <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mb-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <p class="text-lg font-medium">No detections yet</p>
                <p class="text-sm">Waiting for birds to visit...</p>
            </div>
        </div>
    {/if}
</div>
