<script lang="ts">
    import { onMount } from 'svelte';
    import { fetchEvents, deleteDetection, type Detection, getThumbnailUrl } from '../api';
    import DetectionCard from '../components/DetectionCard.svelte';
    import SpeciesDetailModal from '../components/SpeciesDetailModal.svelte';

    let events: Detection[] = $state([]);
    let loading = $state(true);
    let error = $state<string | null>(null);
    let deleting = $state(false);

    let limit = $state(24);
    let offset = $state(0);
    let hasMore = $state(true);

    // Date filters
    type DatePreset = 'all' | 'today' | 'week' | 'month' | 'custom';
    let datePreset = $state<DatePreset>('all');
    let customStartDate = $state('');
    let customEndDate = $state('');

    // Computed date range based on preset
    let dateRange = $derived(() => {
        const today = new Date();
        const formatDate = (d: Date) => d.toISOString().split('T')[0];

        switch (datePreset) {
            case 'today':
                return { start: formatDate(today), end: formatDate(today) };
            case 'week': {
                const weekAgo = new Date(today);
                weekAgo.setDate(weekAgo.getDate() - 7);
                return { start: formatDate(weekAgo), end: formatDate(today) };
            }
            case 'month': {
                const monthAgo = new Date(today);
                monthAgo.setDate(monthAgo.getDate() - 30);
                return { start: formatDate(monthAgo), end: formatDate(today) };
            }
            case 'custom':
                return { start: customStartDate || undefined, end: customEndDate || undefined };
            default:
                return { start: undefined, end: undefined };
        }
    });

    // Filters
    let speciesFilter = $state('');
    let cameraFilter = $state('');
    let sortOrder = $state<'newest' | 'oldest' | 'confidence'>('newest');

    // Derived unique values for filters
    let uniqueSpecies = $derived([...new Set(events.map(e => e.display_name))].sort());
    let uniqueCameras = $derived([...new Set(events.map(e => e.camera_name))].sort());

    // Filtered and sorted events
    let filteredEvents = $derived(() => {
        let result = [...events];

        if (speciesFilter) {
            result = result.filter(e => e.display_name === speciesFilter);
        }

        if (cameraFilter) {
            result = result.filter(e => e.camera_name === cameraFilter);
        }

        switch (sortOrder) {
            case 'oldest':
                result.sort((a, b) => new Date(a.detection_time).getTime() - new Date(b.detection_time).getTime());
                break;
            case 'confidence':
                result.sort((a, b) => b.score - a.score);
                break;
            default: // newest
                result.sort((a, b) => new Date(b.detection_time).getTime() - new Date(a.detection_time).getTime());
        }

        return result;
    });

    // Selected event for modal
    let selectedEvent = $state<Detection | null>(null);
    let selectedSpecies = $state<string | null>(null);

    onMount(async () => {
        await loadEvents();
    });

    async function loadEvents(append = false) {
        loading = true;
        error = null;
        try {
            const range = dateRange();
            const newEvents = await fetchEvents({
                limit,
                offset: append ? offset : 0,
                startDate: range.start,
                endDate: range.end
            });
            if (append) {
                events = [...events, ...newEvents];
            } else {
                events = newEvents;
                offset = 0;
            }
            hasMore = newEvents.length === limit;
            offset += newEvents.length;
        } catch (e) {
            error = 'Failed to load events';
        } finally {
            loading = false;
        }
    }

    function handleDatePresetChange(preset: DatePreset) {
        datePreset = preset;
        // Reset pagination when date filter changes
        offset = 0;
        loadEvents(false);
    }

    function applyCustomDateRange() {
        datePreset = 'custom';
        offset = 0;
        loadEvents(false);
    }

    function loadMore() {
        loadEvents(true);
    }

    function clearFilters() {
        speciesFilter = '';
        cameraFilter = '';
        sortOrder = 'newest';
    }

    async function handleDelete() {
        if (!selectedEvent) return;
        if (!confirm(`Delete this ${selectedEvent.display_name} detection?`)) return;

        deleting = true;
        try {
            await deleteDetection(selectedEvent.frigate_event);
            // Remove from local list
            events = events.filter(e => e.frigate_event !== selectedEvent?.frigate_event);
            selectedEvent = null;
        } catch (e) {
            console.error('Failed to delete detection', e);
            alert('Failed to delete detection');
        } finally {
            deleting = false;
        }
    }
</script>

<div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <h2 class="text-2xl font-bold text-slate-900 dark:text-white">Events</h2>

        <div class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
            <span>{filteredEvents().length} events</span>
            {#if speciesFilter || cameraFilter}
                <button
                    onclick={clearFilters}
                    class="text-teal-500 hover:text-teal-600"
                >
                    Clear filters
                </button>
            {/if}
        </div>
    </div>

    <!-- Date Filters -->
    <div class="flex flex-wrap items-center gap-2">
        <span class="text-sm text-slate-500 dark:text-slate-400">Date:</span>
        {#each [
            { value: 'all', label: 'All Time' },
            { value: 'today', label: 'Today' },
            { value: 'week', label: 'Week' },
            { value: 'month', label: 'Month' },
        ] as preset}
            <button
                onclick={() => handleDatePresetChange(preset.value as DatePreset)}
                class="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors
                       {datePreset === preset.value
                           ? 'bg-teal-500 text-white'
                           : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700'}"
            >
                {preset.label}
            </button>
        {/each}
        <button
            onclick={() => datePreset = 'custom'}
            class="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors
                   {datePreset === 'custom'
                       ? 'bg-teal-500 text-white'
                       : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700'}"
        >
            Custom
        </button>
    </div>

    <!-- Custom Date Range -->
    {#if datePreset === 'custom'}
        <div class="flex flex-wrap items-center gap-3 p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
            <div class="flex items-center gap-2">
                <label class="text-sm text-slate-600 dark:text-slate-400">From:</label>
                <input
                    type="date"
                    bind:value={customStartDate}
                    class="px-3 py-1.5 rounded-lg border border-slate-300 dark:border-slate-600
                           bg-white dark:bg-slate-800 text-slate-900 dark:text-white text-sm"
                />
            </div>
            <div class="flex items-center gap-2">
                <label class="text-sm text-slate-600 dark:text-slate-400">To:</label>
                <input
                    type="date"
                    bind:value={customEndDate}
                    class="px-3 py-1.5 rounded-lg border border-slate-300 dark:border-slate-600
                           bg-white dark:bg-slate-800 text-slate-900 dark:text-white text-sm"
                />
            </div>
            <button
                onclick={applyCustomDateRange}
                class="px-4 py-1.5 rounded-lg text-sm font-medium bg-teal-500 text-white hover:bg-teal-600 transition-colors"
            >
                Apply
            </button>
        </div>
    {/if}

    <!-- Species/Camera/Sort Filters -->
    <div class="flex flex-wrap gap-3">
        <select
            bind:value={speciesFilter}
            class="px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600
                   bg-white dark:bg-slate-800 text-slate-900 dark:text-white text-sm
                   focus:ring-2 focus:ring-teal-500 focus:border-transparent"
        >
            <option value="">All Species</option>
            {#each uniqueSpecies as species}
                <option value={species}>{species}</option>
            {/each}
        </select>

        <select
            bind:value={cameraFilter}
            class="px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600
                   bg-white dark:bg-slate-800 text-slate-900 dark:text-white text-sm
                   focus:ring-2 focus:ring-teal-500 focus:border-transparent"
        >
            <option value="">All Cameras</option>
            {#each uniqueCameras as camera}
                <option value={camera}>{camera}</option>
            {/each}
        </select>

        <select
            bind:value={sortOrder}
            class="px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600
                   bg-white dark:bg-slate-800 text-slate-900 dark:text-white text-sm
                   focus:ring-2 focus:ring-teal-500 focus:border-transparent"
        >
            <option value="newest">Newest First</option>
            <option value="oldest">Oldest First</option>
            <option value="confidence">Highest Confidence</option>
        </select>
    </div>

    {#if error}
        <div class="p-4 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 border border-red-200 dark:border-red-800">
            {error}
            <button onclick={() => loadEvents()} class="ml-2 underline">Retry</button>
        </div>
    {/if}

    {#if loading && events.length === 0}
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {#each [1, 2, 3, 4, 5, 6, 7, 8] as _}
                <div class="aspect-[4/3] bg-slate-100 dark:bg-slate-800 rounded-xl animate-pulse"></div>
            {/each}
        </div>
    {:else if filteredEvents().length === 0}
        <div class="text-center py-16">
            <span class="text-6xl mb-4 block">🔍</span>
            <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-2">No events found</h3>
            <p class="text-slate-500 dark:text-slate-400">
                {#if speciesFilter || cameraFilter}
                    Try adjusting your filters
                {:else}
                    No bird detections yet
                {/if}
            </p>
        </div>
    {:else}
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {#each filteredEvents() as event (event.frigate_event)}
                <DetectionCard
                    detection={event}
                    onclick={() => selectedEvent = event}
                />
            {/each}
        </div>

        {#if hasMore && !speciesFilter && !cameraFilter}
            <div class="flex justify-center pt-4">
                <button
                    onclick={loadMore}
                    disabled={loading}
                    class="px-6 py-3 rounded-lg font-medium text-teal-600 dark:text-teal-400
                           bg-teal-50 dark:bg-teal-900/20 hover:bg-teal-100 dark:hover:bg-teal-900/40
                           disabled:opacity-50 transition-colors"
                >
                    {loading ? 'Loading...' : 'Load More'}
                </button>
            </div>
        {/if}
    {/if}
</div>

<!-- Detail Modal -->
{#if selectedEvent}
    <div
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
        onclick={() => selectedEvent = null}
        onkeydown={(e) => e.key === 'Escape' && (selectedEvent = null)}
        role="dialog"
        tabindex="-1"
    >
        <div
            class="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-hidden
                   border border-slate-200 dark:border-slate-700"
            onclick={(e) => e.stopPropagation()}
            onkeydown={(e) => e.stopPropagation()}
            role="document"
            tabindex="-1"
        >
            <!-- Image with overlay -->
            <div class="relative aspect-video bg-slate-100 dark:bg-slate-700">
                <img
                    src={getThumbnailUrl(selectedEvent.frigate_event)}
                    alt={selectedEvent.display_name}
                    class="w-full h-full object-cover"
                />
                <!-- Gradient overlay with species name -->
                <div class="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent"></div>
                <div class="absolute bottom-0 left-0 right-0 p-4">
                    <h3 class="text-2xl font-bold text-white drop-shadow-lg">
                        {selectedEvent.display_name}
                    </h3>
                    <p class="text-white/80 text-sm mt-1">
                        {new Date(selectedEvent.detection_time).toLocaleDateString(undefined, {
                            weekday: 'short', month: 'short', day: 'numeric', year: 'numeric'
                        })} at {new Date(selectedEvent.detection_time).toLocaleTimeString(undefined, {
                            hour: '2-digit', minute: '2-digit'
                        })}
                    </p>
                </div>
                <!-- Close button -->
                <button
                    onclick={() => selectedEvent = null}
                    class="absolute top-3 right-3 w-8 h-8 rounded-full bg-black/40 text-white/90
                           flex items-center justify-center hover:bg-black/60 transition-colors"
                    aria-label="Close"
                >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>

            <div class="p-5">
                <!-- Confidence bar -->
                <div class="mb-4">
                    <div class="flex items-center justify-between mb-1.5">
                        <span class="text-sm font-medium text-slate-600 dark:text-slate-400">Confidence</span>
                        <span class="text-sm font-bold text-slate-900 dark:text-white">
                            {(selectedEvent.score * 100).toFixed(1)}%
                        </span>
                    </div>
                    <div class="h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                        <div
                            class="h-full rounded-full transition-all duration-500
                                   {selectedEvent.score >= 0.8 ? 'bg-emerald-500' :
                                    selectedEvent.score >= 0.6 ? 'bg-teal-500' :
                                    selectedEvent.score >= 0.4 ? 'bg-amber-500' : 'bg-red-500'}"
                            style="width: {selectedEvent.score * 100}%"
                        ></div>
                    </div>
                </div>

                <!-- Camera info -->
                <div class="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400 mb-5">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                              d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    <span class="font-medium">{selectedEvent.camera_name}</span>
                </div>

                <!-- Action buttons -->
                <div class="flex gap-2">
                    <button
                        onclick={() => {
                            selectedSpecies = selectedEvent?.display_name ?? null;
                            selectedEvent = null;
                        }}
                        class="flex-1 px-4 py-2.5 text-sm font-medium text-white
                               bg-teal-500 hover:bg-teal-600 rounded-lg transition-colors
                               flex items-center justify-center gap-2"
                    >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                  d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Species Info
                    </button>
                    <button
                        onclick={handleDelete}
                        disabled={deleting}
                        class="px-4 py-2.5 text-sm font-medium text-red-600 dark:text-red-400
                               bg-red-50 dark:bg-red-900/20 rounded-lg
                               hover:bg-red-100 dark:hover:bg-red-900/40 transition-colors
                               disabled:opacity-50 disabled:cursor-not-allowed
                               flex items-center justify-center gap-2"
                    >
                        {#if deleting}
                            <svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                        {:else}
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                        {/if}
                        {deleting ? 'Deleting...' : 'Delete'}
                    </button>
                </div>
            </div>
        </div>
    </div>
{/if}

<!-- Species Detail Modal -->
{#if selectedSpecies}
    <SpeciesDetailModal
        speciesName={selectedSpecies}
        onclose={() => selectedSpecies = null}
    />
{/if}
