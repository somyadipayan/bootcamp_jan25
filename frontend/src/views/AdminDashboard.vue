<template>
    <NavBar />
    <h1 class="page-title">Admin Dashboard</h1>
    <!-- // Search bar
    <div class="search-bar">
        <input type="text" placeholder="Search users..." v-model="searchQuery">
    </div> -->
    <h2 class="my-5">App Statistics</h2>
    <div class="row">
        <div class="col-md-6 mb-4">
            <div class="statistics mt-5">
                <div class="stat-card card mb-3" v-for="(value, key) in stats" :key="key">
                    <div class="card-body">
                        <h5 class="card-title">{{ key }}</h5>
                        <p class="card-text">{{ value }}</p>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-6 mb-4 d-flex justify-content-center align-items-center">
            <div class="graph">
                <img :src="graphSrc" style="height: 80%;" alt="Graph" class="img-fluid rounded shadow" />
            </div>
        </div>
    </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue';
export default {
    name: 'AdminDashboard',
    data(){
        return {
            // searchQuery: '',
            stats: {},
            graphSrc: ''
        }
    },
    components: {
        NavBar
    },
    mounted() {
        // this.getactiveusers();
        this.fetchStats();
        this.fetchGraph();
    },
    methods: {
        async fetchStats() {
            try {
                const response = await fetch('http://localhost:5000/admin/statistics', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                    },
                });
                const data = await response.json();
                if (response.ok) {
                    this.stats = data;
                } else {
                    console.error(data.message);
                }
            } catch (error) {
                console.error('Failed to fetch stats:', error);
            }
        },
        async fetchGraph() {
            try {
                const response = await fetch('http://localhost:5000/admin/statistics/graph', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                    },
                });
                // const data = await response.json();
                if (response.ok) {
                    const blob = await response.blob();
                    this.graphSrc = URL.createObjectURL(blob);
                } else {
                    console.error(data.message);
                }
            } catch (error) {
                console.error('Failed to fetch graph:', error);
            }
        },
    }
}
</script>

<style scoped>
.statistics {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    gap: 20px;
    margin: 20%;
}

.stat-card {
    background: #ffffff;
    border: 1px solid #e9ecef;
    border-radius: 12px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stat-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.stat-card .card-body{
    padding: 20px;
}

.graph img{
    max-width: 100%;
    height: auto;
    border-radius: 12px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    border: 1px solid #e9ecef;
}
</style>