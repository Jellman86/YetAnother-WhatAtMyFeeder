<script lang="ts">
  import { onMount } from 'svelte';
  import DetectionCard from './lib/components/DetectionCard.svelte';
  import Events from './lib/components/Events.svelte';
  import Settings from './lib/components/Settings.svelte';
  import Species from './lib/components/Species.svelte';
  import { fetchEvents } from './lib/api';

  // Simple Router state
  let currentRoute = $state('/');

  function navigate(path: string) {
      currentRoute = path;
      window.history.pushState(null, '', path);
  }

  // Handle back button
  onMount(() => {
      const handlePopState = () => {
          currentRoute = window.location.pathname;
      };
      window.addEventListener('popstate', handlePopState);
      return () => window.removeEventListener('popstate', handlePopState);
  });
  
  // Dashboard Logic
  let detections = $state([]);
  let connected = $state(false);

  async function loadInitial() {
      try {
          detections = await fetchEvents();
      } catch (e) {
          console.error(e);
      }
  }

  function connectSSE() {
      const evtSource = new EventSource('/api/sse');
      
      evtSource.onopen = () => {
          connected = true;
          console.log("SSE Connected");
      };

      evtSource.onmessage = (event) => {
          try {
             const payload = JSON.parse(event.data);
             if (payload.type === 'detection') {
                 const newDet = {
                     frigate_event: payload.data.frigate_event,
                     display_name: payload.data.display_name,
                     score: payload.data.score,
                     detection_time: payload.data.timestamp,
                     camera_name: payload.data.camera
                 };
                 detections = [newDet, ...detections];
             }
          } catch (e) {
              console.error("SSE Error", e);
          }
      };

      evtSource.onerror = (err) => {
          console.error("SSE Connection Error", err);
          connected = false;
          evtSource.close();
          setTimeout(connectSSE, 5000);
      };
  }

  onMount(() => {
      const path = window.location.pathname;
      currentRoute = path === '' ? '/' : path;
      loadInitial();
      connectSSE();
  });
</script>

<div class="min-h-screen bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-white font-sans">
  <!-- Header -->
  <header class="bg-white dark:bg-gray-800 shadow sticky top-0 z-10">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div class="flex items-center gap-3">
              <h1 class="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-500 to-teal-400">
                  WhosAtMyFeeder
              </h1>
              {#if connected}
                  <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse" title="Live"></span>
              {:else}
                  <span class="w-2 h-2 rounded-full bg-red-500" title="Disconnected"></span>
              {/if}
          </div>
          <nav class="flex gap-4">
              <button class="hover:text-blue-500 font-medium {currentRoute === '/' ? 'text-blue-500' : ''}" onclick={() => navigate('/')}>Dashboard</button>
              <button class="hover:text-blue-500 font-medium {currentRoute === '/events' ? 'text-blue-500' : ''}" onclick={() => navigate('/events')}>Explorer</button>
              <button class="hover:text-blue-500 font-medium {currentRoute === '/species' ? 'text-blue-500' : ''}" onclick={() => navigate('/species')}>Leaderboard</button>
              <button class="hover:text-blue-500 font-medium {currentRoute === '/settings' ? 'text-blue-500' : ''}" onclick={() => navigate('/settings')}>Settings</button>
          </nav>
      </div>
  </header>

  <!-- Main Content -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {#if currentRoute === '/' || currentRoute === ''}
          <!-- Dashboard View -->
          <div class="mb-8">
              <h2 class="text-2xl font-bold mb-4">Live Detections</h2>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
              {#each detections as detection (detection.frigate_event || detection.id)}
                  <DetectionCard {detection} />
              {/each}
              
              {#if detections.length === 0}
                  <div class="col-span-full text-center py-12 text-gray-500">
                      No detections yet. Waiting for birds...
                  </div>
              {/if}
          </div>
      {:else if currentRoute === '/events'}
          <Events />
      {:else if currentRoute === '/species'}
          <Species />
      {:else if currentRoute === '/settings'}
           <Settings />
      {/if}
  </main>
</div>
