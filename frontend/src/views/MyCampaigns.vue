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
                        <p class="card-text">Start Date: {{ campaign.start_date }}</p>
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
                            <button @click="openRequestModal(campaign.id)" class="btn btn-dark">Send Request</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <button class="btn btn-primary mt-3" @click="createCampaign()">Create Campaign</button>
        <!-- REQUEST MODAL -->

        <div class="modal fade" id="requestModal" tabindex="-1" aria-labelledby="requestModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="requestModalLabel">Send Request to Influencer</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <form @submit.prevent="sendRequest">
                            <!-- Search Bar -->
                            <div class="mb-3">
                                <input type="text" v-model="searchQuery" class="form-control"
                                    placeholder="Search Influencers">
                            </div>
                            <!-- Filters -->
                            <!-- category -->
                            <div class="mb-3">
                                <label for="category">Category:</label>
                                <select id="category" v-model="filters.category" class="form-select">
                                    <option value="">All Category</option>
                                    <option v-for="category in uniqueCategories" :key="category" :value="category">
                                        {{ category }}
                                    </option>
                                </select>
                            </div>
                            <!-- reach -->
                            <div class="mb-3">
                                <label for="reach">Reach:</label>
                                <select id="reach" v-model="filters.reach" class="form-select">
                                    <option value="">All Reach</option>
                                    <option value="low">Low</option>
                                    <option value="medium">Medium</option>
                                    <option value="high">High</option>
                                </select>
                            </div>

                            <!-- Influencer Selection -->
                            <div class="mb-3">
                                <label for="influencer" class="form-label">Influencer:</label>
                                <select v-model="requestForm.influencerId" class="form-select" id="influencer"
                                    @change="updateInfluencerDetails" required>
                                    <option v-for="influencer in filteredInfluencers" :key="influencer.id"
                                        :value="influencer.id">
                                        {{ influencer.name }} ({{ influencer.category }})
                                    </option>
                                </select>
                            </div>
                            <!-- Display selected Influencer Details -->
                            <div v-if="selectedInfluencer">
                                <p><strong>Name:</strong> {{ selectedInfluencer.name }}</p>
                                <p><strong>Category:</strong> {{ selectedInfluencer.category }}</p>
                                <p><strong>Reach:</strong> {{ selectedInfluencer.reach }} | {{
                                    getReachCategory(selectedInfluencer.reach) }}</p>
                                <p><strong>Niche:</strong> {{ selectedInfluencer.niche }}</p>
                                <p><strong>Previous Collaborations:</strong>{{ selectedInfluencer.previous_collaborations
                                    ? selectedInfluencer.previous_collaborations : 'N/A'}}</p>
                            </div>
                            <div class="mb-3">
                                <label for="requirements" class="form-label">Requirements:</label>
                                <textarea v-model="requestForm.requirements" class="form-control" id="requirements"
                                    rows="3" required></textarea>
                            </div>
                            <div class="mb-3">
                                <label for="paymentAmount" class="form-label">Payment Amount:</label>
                                <input v-model="requestForm.paymentAmount" type="number" class="form-control"
                                    id="paymentAmount" required>
                            </div>
                            <button type="submit" class="btn btn-primary">Send Request</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>

    </div>

</template>

<script>
import NavBar from '@/components/NavBar.vue';
export default {
    components: { NavBar },
    name: 'MyCampaigns',
    data() {
        return {
            campaigns: [],
            searchQuery: '',
            filters: {
                category: '',
                reach: ''
            },
            influencers: [],
            selectedInfluencer: null,
            requestForm: {
                campaignId: '',
                influencerId: '',
                requirements: '',
                paymentAmount: ''
            }
        }
    },
    mounted() {
        this.fetchCampaigns();
        this.fetchInfluencers();
    },
    computed: {
        uniqueCategories() {
            const categories = this.influencers.map(influencer => influencer.category);
            return [...new Set(categories)];
        },
        filteredInfluencers() {
            return this.influencers.filter(influencer => {
                const matchesSearch = influencer.name.toLowerCase().includes(this.searchQuery.toLowerCase());
                const matchesCategory = this.filters.category ? influencer.category === this.filters.category : true;
                const matchesReach = this.filters.reach ? this.getReachCategory(influencer.reach) === this.filters.reach : true;
                return matchesSearch && matchesCategory && matchesReach;
            });
        }
    },
    methods: {
        async fetchInfluencers() {
            try {
                const response = await fetch('http://localhost:5000/all_influencers', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                const data = await response.json();
                if (response.ok) {
                    this.influencers = data;
                } else {
                    alert(data.error);
                }
            } catch (error) {
                console.error(error);
            }
        },
        async fetchCampaigns() {
            try {
                const response = await fetch('http://localhost:5000/my-campaigns', {
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
        },
        openRequestModal(campaignId) {
            this.requestForm.campaignId = campaignId;
            const requestModal = new bootstrap.Modal(document.getElementById('requestModal'));
            requestModal.show();
        },
        getReachCategory(reach) {
            if (reach < 10000) return 'low';
            if (reach < 50000) return 'medium';
            return 'high';
        },
        updateInfluencerDetails() {
            this.selectedInfluencer = this.influencers.find(influencer => influencer.id === this.requestForm.influencerId);
        },

        async sendRequest() {
            try {
                const response = await fetch('http://localhost:5000/sponsor/send-ad-request', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                    },
                    body: JSON.stringify(this.requestForm)
                });
                const data = await response.json();
                if (response.ok) {
                    alert(data.message);
                    const requestModal = new bootstrap.Modal(document.getElementById('requestModal'));
                    requestModal.hide();
                } else {
                    alert(data.error);
                }
            } catch (error) {
                console.error(error);
            }
        },

    }
}
</script>