<template>
    <NavBar />
    <div class="container mt-5">
        <h2>My Campaigns</h2>
        <div class="row">
            <div class="col-md-3 mb-4" v-for="campaign in campaigns" :key="campaign.id">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">{{ campaign.name }}</h5>
                        <p class="card-text">Description: {{ campaign.description }}</p>
                        <p class="card-text">Satrt Date: {{ campaign.start_date }}</p>
                        <p class="card-text">End Date: {{ campaign.end_date }}</p>
                        <p class="card-text">Budget: {{ campaign.budget }}</p>
                        <p class="card-text">Visibility: {{ campaign.visibility }}</p>
                        <p class="card-text">Goals: {{ campaign.goals }}</p>
                    </div>
                    <div class="card-footer">
                        <div class="btn-group">
                            <router-link :to="{ name: 'editcampaign', params: { id: campaign.id } }"
                                class="btn btn-dark">Edit</router-link>
                            <button class="btn btn-dark" @click="deleteCampaign(campaign.id)">Delete</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <button class="btn btn-primary mt-3" @click="createCampaign()">Create Campaign</button>
    </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue';
export default {
    components: { NavBar },
    name: 'MyCampaigns',
    data() {
        return {
            campaigns: []
        }
    },
    mounted() {
        this.fetchCampaigns();
    },
    methods: {
        async fetchCampaigns() {
            try {
                const response = await fetch('http://localhost:5000/my-campaigns',{
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                    }
                });
                const data = await response.json();
                console.log(data);
                if (response.ok) {
                    this.campaigns = data;
                } else {
                    alert(data.error);
                }
            } catch (error) {
                console.error(error);
            }
        },
        createCampaign() {
            this.$router.push('/create-campaign');
        },
        async deleteCampaign(campaignId) {
            try {
                const response = await fetch(`http://localhost:5000/campaign/${campaignId}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                    }
                });
                const data = await response.json();
                if (response.ok) {
                    alert(data.message);
                    this.fetchCampaigns();
                } else {
                    alert(data.error);
                }
            } catch (error) {
                console.error(error);
            }
        }
    }
}
</script>