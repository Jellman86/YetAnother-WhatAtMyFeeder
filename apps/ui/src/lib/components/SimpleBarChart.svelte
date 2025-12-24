<script lang="ts">
    interface Props {
        data: number[];
        labels: string[];
        title: string;
        color?: string;
    }

    let { data, labels, title, color = 'bg-teal-500' }: Props = $props();

    let maxValue = $derived(Math.max(...data, 1));
    let hoveredIndex = $state<number | null>(null);
</script>

<div class="w-full">
    <h4 class="text-sm font-medium text-slate-700 dark:text-slate-300 mb-3">{title}</h4>

    <div class="flex items-end gap-1 h-32">
        {#each data as value, i}
            <div
                class="flex-1 flex flex-col items-center justify-end h-full group relative"
                onmouseenter={() => hoveredIndex = i}
                onmouseleave={() => hoveredIndex = null}
                role="img"
                aria-label="{labels[i]}: {value}"
            >
                <!-- Tooltip -->
                {#if hoveredIndex === i && value > 0}
                    <div class="absolute -top-8 left-1/2 -translate-x-1/2 px-2 py-1 rounded bg-slate-800 text-white text-xs whitespace-nowrap z-10">
                        {value}
                    </div>
                {/if}

                <!-- Bar -->
                <div
                    class="{color} w-full rounded-t transition-all duration-200
                           {hoveredIndex === i ? 'opacity-100' : 'opacity-80'}
                           {value === 0 ? 'bg-slate-200 dark:bg-slate-700' : ''}"
                    style="height: {value > 0 ? Math.max((value / maxValue) * 100, 4) : 2}%"
                ></div>

                <!-- Label -->
                <span class="text-[10px] text-slate-500 dark:text-slate-400 mt-1 truncate w-full text-center">
                    {labels[i]}
                </span>
            </div>
        {/each}
    </div>
</div>
