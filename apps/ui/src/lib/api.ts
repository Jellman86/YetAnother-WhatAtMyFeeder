export interface Detection {
    id?: number;
    frigate_event: string;
    display_name: string;
    score: number;
    detection_time: string;
    camera_name: string;
    detection_index?: number;
    category_name?: string;
}

export async function fetchEvents(limit = 50, offset = 0): Promise<Detection[]> {
    const response = await fetch(`/api/events?limit=${limit}&offset=${offset}`);
    if (!response.ok) {
        throw new Error(`Failed to fetch events: ${response.statusText}`);
    }
    return response.json();
}

export async function fetchSpecies(): Promise<{ species: string; count: number }[]> {
    const response = await fetch('/api/species');
    if (!response.ok) {
        throw new Error(`Failed to fetch species: ${response.statusText}`);
    }
    return response.json();
}

export interface Settings {
    frigate_url: string;
    mqtt_server: string;
    classification_threshold: number;
}

export async function fetchSettings(): Promise<Settings> {
    const response = await fetch('/api/settings');
    if (!response.ok) {
        throw new Error(`Failed to fetch settings: ${response.statusText}`);
    }
    return response.json();
}

export async function updateSettings(settings: Settings): Promise<void> {
    const response = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings),
    });
    if (!response.ok) {
        throw new Error(`Failed to update settings: ${response.statusText}`);
    }
}
