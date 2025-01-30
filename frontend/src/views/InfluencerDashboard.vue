<template>
       <NavBar/>
    <div class="container mt-5">
        <!-- Public Campaigns Section -->
        <h2 class="text-center">Public Campaigns</h2>
        <div class="row mb-4">
            <div class="col-md-4 offset-md-4">
                <input v-model="searchQuery" type="text" class="form-control" placeholder="Search campaigns..."
                    @input="filterCampaigns">
            </div>
        </div>
        <div class="row">
            <div v-for="campaign in filteredCampaigns" :key="campaign.id" class="col-md-3 mb-4">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">{{ campaign.name }}</h5>
                        <p class="card-text">{{ campaign.description }}</p>
                        <button class="btn btn-primary" @click="openRequestModal(campaign.id)">Send Request</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- My Ad Requests Section -->
        <h2 class="text-center mt-5">My Ad Requests</h2>
        <div v-if="adRequests.length > 0" class="row">
            <div v-for="request in adRequests" :key="request.id" class="col-md-4 mb-4">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">{{ request.name }}</h5>
                        <p class="card-text"><strong>From:</strong> {{ request.sponsor }}</p>
                        <p class="card-text"><strong>Requirements:</strong> {{ request.requirements }}</p>
                        <p class="card-text"><strong>Payment:</strong> ${{ request.payment_amount }}</p>
                        <p class="card-text"><strong>Status:</strong> {{ request.status }}</p>
                        <div v-if = "request.status === 'Pending' || request.status === 'Negotiation'">
                        <div v-if="request.sent_by === 'sponsor'">
                            <button class="btn btn-success me-2" @click="acceptRequest(request.id)">Accept</button>
                            <button class="btn btn-danger me-2" @click="rejectRequest(request.id)">Reject</button>
                            <button class="btn btn-warning"
                                @click="negotiate(request.id)">Negotiate</button>
                        </div>
                        <div v-else>
                            <button class="btn btn-dark me-2" disabled>Request Sent</button>
                        </div>
                        </div>
                        <div v-else>
                            <button class="btn btn-dark me-2" disabled>Active</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div v-else>
            <p class="text-center">No ad requests available.</p>
        </div>

        <!-- Send Request Modal -->
        <div class="modal fade" id="requestModal" tabindex="-1" aria-labelledby="requestModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="requestModalLabel">Send Ad Request</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <form @submit.prevent="sendAdRequest">
                            <div class="mb-3">
                                <label for="requirements" class="form-label">Requirements</label>
                                <input v-model="requestForm.requirements" type="text" class="form-control"
                                    id="requirements" required>
                            </div>
                            <div class="mb-3">
                                <label for="paymentAmount" class="form-label">Payment Amount</label>
                                <input v-model="requestForm.paymentAmount" type="number" class="form-control"
                                    id="paymentAmount" required>
                            </div>
                            <button type="submit" class="btn btn-success">Submit</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>

        <!-- Negotiate Payment Modal -->
        <!-- <div class="modal fade" id="negotiateModal" tabindex="-1" aria-labelledby="negotiateModalLabel"
            aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="negotiateModalLabel">Negotiate Payment Amount</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <form @submit.prevent="negotiatePayment">
                            <div class="mb-3">
                                <label for="negotiatedAmount" class="form-label">New Payment Amount</label>
                                <input v-model="negotiationForm.newPaymentAmount" type="number" class="form-control"
                                    id="negotiatedAmount" required>
                            </div>
                            <button type="submit" class="btn btn-warning">Submit</button>
                        </form>
                    </div>
                </div>
            </div> 
        </div>-->
    </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue';
export default {
  components: {
    NavBar
  },
    data() {
        return {
            publicCampaigns: [],
            adRequests: [],
            requestForm: {
                campaign_id: null,
                messages: '',
                requirements: '',
                paymentAmount: '',
            },
            // negotiationForm: {
            //     requestId: null,
            //     newPaymentAmount: '',
            // },
            searchQuery: '', // Added for search functionality
            filteredCampaigns: [], // To store filtered campaigns
        };
    },
    methods: {

        fetchPublicCampaigns() {
            fetch('http://localhost:5000/public_campaigns', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                },
            })
                .then(response => response.json())
                .then(data => {
                    this.publicCampaigns = data;
                    this.filteredCampaigns = data; // Initialize with all campaigns
                })
                .catch(error => console.error('Error fetching campaigns:', error));
        },


        fetchAdRequests() {
            fetch('http://localhost:5000/influencer/ad-requests', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                },
            })
                .then(response => response.json())
                .then(data => {
                    this.adRequests = data;
                    console.log(this.adRequests);
                })
                .catch(error => console.error('Error fetching ad requests:', error));
        },

        filterCampaigns() {
            const query = this.searchQuery.toLowerCase();
            this.filteredCampaigns = this.publicCampaigns.filter(campaign =>
                campaign.name.toLowerCase().includes(query) ||
                campaign.description.toLowerCase().includes(query)
            );
        },
        openRequestModal(campaignId) {
            this.requestForm.campaign_id = campaignId;
            const requestModal = new bootstrap.Modal(document.getElementById('requestModal'));
            requestModal.show();
        },
        sendAdRequest() {
            fetch('http://localhost:5000/influencer/send_ad_request', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                },
                body: JSON.stringify(this.requestForm),
            })
                .then(response => {
                    if (response.ok) {
                        alert('Ad request sent successfully');
                        this.resetRequestForm();
                        const requestModal = bootstrap.Modal.getInstance(document.getElementById('requestModal'));
                        requestModal.hide();
                        this.fetchAdRequests(); // Refresh the ad requests list
                    } else {
                        return response.json().then(data => {
                            alert(data.message || 'Failed to send request');
                        });
                    }
                })
                .catch(error => console.error('Error sending ad request:', error));
        },
        resetRequestForm() {
            this.requestForm = {
                campaign_id: null,
                messages: '',
                requirements: '',
                paymentAmount: '',
            };
        },
        // openNegotiateModal(requestId, currentPaymentAmount) {
        //     this.negotiationForm.requestId = requestId;
        //     this.negotiationForm.newPaymentAmount = currentPaymentAmount;
        //     const negotiateModal = new bootstrap.Modal(document.getElementById('negotiateModal'));
        //     negotiateModal.show();
        // },
        // Method to accept an ad request
        acceptRequest(requestId) {
            fetch('http://localhost:5000/accept_ad_request', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                },
                body: JSON.stringify({ ad_request_id: requestId }),
            })
                .then(response => {
                    if (response.ok) {
                        alert('Ad request accepted successfully');
                        this.fetchAdRequests(); // Refresh the ad requests list
                    } else {
                        return response.json().then(data => {
                            alert(data.message || 'Failed to accept request');
                        });
                    }
                })
                .catch(error => console.error('Error accepting ad request:', error));
        },

        // // Method to reject an ad request
        rejectRequest(requestId) {
            fetch('http://localhost:5000/reject_ad_request', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                },
                body: JSON.stringify({ ad_request_id: requestId }),
            })
                .then(response => {
                    if (response.ok) {
                        alert('Ad request rejected successfully');
                        this.fetchAdRequests(); // Refresh the ad requests list
                    } else {
                        return response.json().then(data => {
                            alert(data.message || 'Failed to reject request');
                        });
                    }
                })
                .catch(error => console.error('Error rejecting ad request:', error));
        },

        // // Method to negotiate a payment amount for an ad request
        // negotiatePayment() {
        //     fetch('http://localhost:5000/negotiate_ad_request', {
        //         method: 'PUT',
        //         headers: {
        //             'Content-Type': 'application/json',
        //             'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        //         },
        //         body: JSON.stringify({
        //             ad_request_id: this.negotiationForm.requestId,
        //             paymentAmount: this.negotiationForm.newPaymentAmount,
        //         }),
        //     })
        //         .then(response => {
        //             if (response.ok) {
        //                 alert('Ad request negotiated successfully');
        //                 this.fetchAdRequests(); // Refresh the ad requests list
        //                 const negotiateModal = bootstrap.Modal.getInstance(document.getElementById('negotiateModal'));
        //                 negotiateModal.hide();
        //             } else {
        //                 return response.json().then(data => {
        //                     alert(data.message || 'Failed to negotiate payment');
        //                 });
        //             }
        //         })
        //         .catch(error => console.error('Error negotiating payment:', error));
        // },
        negotiate(id){
            this.$router.push({ name: 'NegotiationPage', params: { id: id } });
        }
    },
    mounted() {
        this.fetchPublicCampaigns();
        this.fetchAdRequests(); // Fetch ad requests on component mount
    },
};
</script>


<style scoped>
.card {
    height: 100%;
}

.card-title {
    font-size: 1.25rem;
}

.card-text {
    font-size: 0.875rem;
    color: #6c757d;
}
</style>