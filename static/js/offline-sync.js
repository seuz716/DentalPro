class OfflineSync {
    constructor(patientPk) {
        this.patientPk = String(patientPk || '0');
        this.dbName = 'dentalpro_offline_db';
        this.storeName = 'pending_ops';
        this.dbVersion = 1;
        this.db = null;
        this.isOnline = navigator.onLine;

        window.addEventListener('online', () => this.handleOnlineChange(true));
        window.addEventListener('offline', () => this.handleOnlineChange(false));
    }

    async init() {
        await this.openDatabase();
        this.updateOnlineStatus(this.isOnline);
        if (this.isOnline) {
            this.processPendingOperations();
        }
        this.initFormInterceptor();
    }

    openDatabase() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.dbVersion);

            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                if (!db.objectStoreNames.contains(this.storeName)) {
                    db.createObjectStore(this.storeName, { keyPath: 'id', autoIncrement: true });
                }
            };

            request.onsuccess = (event) => {
                this.db = event.target.result;
                resolve(this.db);
            };

            request.onerror = (event) => {
                console.error('OfflineSync IndexedDB error:', event.target.error);
                reject(event.target.error);
            };
        });
    }

    getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }

    updateOnlineStatus(isOnline) {
        this.isOnline = isOnline;
        this.toggleOfflineBanner(!isOnline);
        if (isOnline) {
            this.processPendingOperations();
        }
    }

    toggleOfflineBanner(show) {
        const banner = document.getElementById('offline-banner');
        if (!banner) return;

        if (show) {
            banner.style.transform = 'translateY(0)';
            banner.style.opacity = '1';
            banner.style.pointerEvents = 'auto';
        } else {
            banner.style.transform = 'translateY(6rem)';
            banner.style.opacity = '0';
            banner.style.pointerEvents = 'none';
        }
    }

    async queueToothUpdate({ fdi, status, notes = '' }) {
        if (!this.db) {
            await this.openDatabase();
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.storeName], 'readwrite');
            const store = transaction.objectStore(this.storeName);
            const payload = {
                patientPk: this.patientPk,
                fdi: Number(fdi),
                status: String(status),
                notes: String(notes || ''),
                timestamp: new Date().toISOString(),
            };

            const request = store.add(payload);
            request.onsuccess = () => {
                console.log('OfflineSync: operación pendiente guardada', payload);
                resolve(payload);
            };
            request.onerror = (event) => {
                console.error('OfflineSync: error al guardar operación', event.target.error);
                reject(event.target.error);
            };
        });
    }

    getAllPending() {
        return new Promise((resolve, reject) => {
            if (!this.db) {
                reject(new Error('IndexedDB no inicializado')); 
                return;
            }

            const transaction = this.db.transaction([this.storeName], 'readonly');
            const store = transaction.objectStore(this.storeName);
            const request = store.getAll();

            request.onsuccess = () => {
                resolve(request.result || []);
            };
            request.onerror = (event) => {
                console.error('OfflineSync: error al leer operaciones pendientes', event.target.error);
                reject(event.target.error);
            };
        });
    }

    deletePendingOperation(id) {
        return new Promise((resolve, reject) => {
            if (!this.db) {
                reject(new Error('IndexedDB no inicializado'));
                return;
            }
            const transaction = this.db.transaction([this.storeName], 'readwrite');
            const store = transaction.objectStore(this.storeName);
            const request = store.delete(id);

            request.onsuccess = () => resolve();
            request.onerror = (event) => reject(event.target.error);
        });
    }

    async processPendingOperations() {
        if (!navigator.onLine) {
            return;
        }
        if (!this.db) {
            await this.openDatabase();
        }

        try {
            const pendingOperations = await this.getAllPending();
            for (const op of pendingOperations) {
                const url = `/pacientes/${this.patientPk}/diente/${op.fdi}/estado/`;
                try {
                    const response = await fetch(url, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': this.getCookie('csrftoken') || ''
                        },
                        body: JSON.stringify({
                            status: op.status,
                            notes: op.notes
                        })
                    });

                    if (response.ok) {
                        const data = await response.json();
                        if (data.success) {
                            await this.deletePendingOperation(op.id);
                            console.log('OfflineSync: operación enviada y eliminada', op);
                        } else {
                            console.warn('OfflineSync: backend rechazó la operación', data);
                        }
                    } else {
                        console.warn('OfflineSync: respuesta no OK', response.status);
                    }
                } catch (error) {
                    console.error('OfflineSync: error al enviar operación pendiente', error);
                    break;
                }
            }
        } catch (error) {
            console.error('OfflineSync: no se pudieron procesar las operaciones pendientes', error);
        }
    }

    initFormInterceptor() {
        const form = document.getElementById('odontogram-3d-htmx-form');
        if (!form) return;

        form.addEventListener('submit', async (event) => {
            if (navigator.onLine) {
                return;
            }

            event.preventDefault();

            const formData = new FormData(form);
            const fdi = formData.get('fdi');
            const status = formData.get('status');
            const notes = formData.get('notes') || '';

            if (!fdi || !status) {
                return;
            }

            await this.queueToothUpdate({ fdi, status, notes });
            this.updateOnlineStatus(false);
        });
    }

    handleOnlineChange(isOnline) {
        this.updateOnlineStatus(isOnline);
    }
}

window.OfflineSync = OfflineSync;
