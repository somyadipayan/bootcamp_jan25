<template>
    <NavBar/>
 <div class="container mt-5">
   <h2>My Campaigns</h2>
   <button class="btn btn-primary mb-3 mt-3" @click="exportCSV">Export CSV Details</button>
   <!-- My Campaigns Section -->
   <div class="row">
     <div v-for="campaign in campaigns" :key="campaign.id" class="col-md-3 mb-4">
       <div class="card">
         <div class="card-body">
           <h5 class="card-title">{{ campaign.name }}</h5>
           <p class="card-text">{{ campaign.description }}</p>
           <p><strong>Start Date:</strong> {{ campaign.start_date }}</p>
           <p><strong>End Date:</strong> {{ campaign.end_date }}</p>
           <p><strong>Budget:</strong> {{ campaign.budget }}</p>
           <p><strong>Visibility:</strong> {{ campaign.visibility }}</p>
           <p><strong>Goals:</strong> {{ campaign.goals }}</p>
           <div class="btn-group">
             <button @click="editCampaign(campaign.id)" class="btn btn-dark">Edit</button>
             <button @click="deleteCampaign(campaign.id)" class="btn btn-dark">Delete</button>
             <button @click="openRequestModal(campaign.id)" class="btn btn-primary">Send Request</button>
           </div>
         </div>
       </div>
     </div>
   </div>

   <!-- New Requests for You Section -->
   <h2 class="mt-5">Requests for You</h2>
   <div class="row">
     <div v-for="request in requestsForYou" :key="request.id" class="col-md-3 mb-4">
       <div class="card">
         <div class="card-body">
           <h5 class="card-title">{{ request.campaign_name }}</h5>
           <p class="card-text"><strong>Influencer:</strong> {{ request.influencer }}</p>
           <p class="card-text"><strong>Requirements:</strong> {{ request.requirements }}</p>
           <p class="card-text"><strong>Payment Amount:</strong> {{ request.payment_amount }}</p>
           <p class="card-text"><strong>Status:</strong> {{ request.status }}</p>
           <div v-if="request.status === 'Pending' || request.status === 'Negotiation'" class="btn-group">
             <div v-if="request.sent_by === 'influencer'" class="btn-group">
               <button @click="acceptAdRequest(request.id)" class="btn btn-success">Accept</button>
               <button @click="rejectAdRequest(request.id)" class="btn btn-danger">Reject</button>
               <button @click="negotiateAdRequest(request.id)" class="btn btn-warning">Negotiate</button>
             </div>
             <div v-else>
               <button class="btn btn-dark me-2" disabled>Request Sent</button>
             </div>
           </div>
           <div v-else>
             <button class="btn btn-success me-2" disabled>Active</button>
           </div>
         </div>
       </div>
     </div>
   </div>

   <!-- Message Section -->
   <div v-if="message" class="alert mt-3" :class="messageClass">{{ message }}</div>

    <!-- Request Modal -->
    <div class="modal fade" id="requestModal" tabindex="-1" aria-labelledby="requestModalLabel" aria-hidden="true">
     <div class="modal-dialog">
       <div class="modal-content">
         <div class="modal-header">
           <h5 class="modal-title" id="requestModalLabel">Send Request to Influencer</h5>
           <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
         </div>
         <div class="modal-body">
           <form @submit.prevent="sendAdRequest">
             <!-- Search Bar -->
             <div class="mb-3">
               <input v-model="searchQuery" type="text" class="form-control" placeholder="Search Influencers...">
             </div>

             <!-- Filters -->
             <div class="mb-3">
               <label for="categoryFilter" class="form-label">Filter by Category</label>
               <select v-model="filters.category" class="form-control" id="categoryFilter">
                 <option value="">All Categories</option>
                 <option v-for="category in uniqueCategories" :key="category" :value="category">
                   {{ category }}
                 </option>
               </select>
             </div>
             <div class="mb-3">
               <label for="reachFilter" class="form-label">Filter by Reach</label>
               <select v-model="filters.reach" class="form-control" id="reachFilter">
                 <option value="">All Reaches</option>
                 <option value="Low">Low</option>
                 <option value="Medium">Medium</option>
                 <option value="High">High</option>
               </select>
             </div>

             <!-- Influencer Selection -->
             <div class="mb-3">
               <label for="influencer" class="form-label">Select Influencer</label>
               <select v-model="requestForm.influencer_id" class="form-control" id="influencer"
                 @change="updateInfluencerDetails" required>
                 <option v-for="influencer in filteredInfluencers" :key="influencer.id" :value="influencer.id">
                   {{ influencer.name }} ({{ influencer.category }})
                 </option>
               </select>
             </div>
             <!-- Displaying Influencer Details -->
             <div v-if="selectedInfluencer" class="influencer-details">
               <p><strong>Name:</strong> {{ selectedInfluencer.name }}</p>
               <p><strong>Category:</strong> {{ selectedInfluencer.category }}</p>
               <p><strong>Reach:</strong> {{ selectedInfluencer.reach }}</p>
               <p><strong>Engagement:</strong> {{ selectedInfluencer.engagement }}</p>
               <p><strong>Previous Collaborations:</strong>
                 {{ selectedInfluencer.previous_collaborations ? selectedInfluencer.previous_collaborations.join(', ')
       : 'None' }}
               </p>
             </div>

             <div class="mb-3">
               <label for="messages" class="form-label">Message</label>
               <textarea v-model="requestForm.messages" class="form-control" id="messages" required></textarea>
             </div>
             <div class="mb-3">
               <label for="requirements" class="form-label">Requirements</label>
               <input v-model="requestForm.requirements" type="text" class="form-control" id="requirements" required>
             </div>
             <div class="mb-3">
               <label for="paymentAmount" class="form-label">Payment Amount</label>
               <input v-model="requestForm.paymentAmount" type="number" class="form-control" id="paymentAmount"
                 required>
             </div>
             <button type="submit" class="btn btn-success">Submit</button>
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
 components: {
   NavBar
 },
 data() {
   return {
     searchQuery: '',
     filters: {
       category: '',
       reach: ''
     },
     campaigns: [],
     influencers: [],
     selectedInfluencer: null,
     requestsForYou: [],
     requestForm: {
       campaign_id: null,
       influencer_id: null,
       messages: '',
       requirements: '',
       paymentAmount: '',
     },
     message: '',
     messageClass: ''
   };
 },
 mounted() {
   this.fetchCampaigns();
   this.fetchInfluencers();
   this.fetchRequestsForYou();
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
  async exportCSV() {
    const response = await fetch('http://localhost:5000/sponsor/csv', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });
  
    if(response.ok) {
      alert("Your CSV Export is ready");
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'campaign_details.csv';
      document.body.appendChild(a);
      a.click();
      a.remove();
    }else{
      console.log("Failed to export CSV");
    }
  },
   async fetchCampaigns() {
     try {
       const response = await fetch('http://localhost:5000/my-campaigns', {
         method: 'GET',
         headers: {
           'Authorization': `Bearer ${localStorage.getItem('access_token')}`
         }
       });
       const data = await response.json();
       if (response.ok) {
         this.campaigns = data;
       } else {
         this.message = data.message;
         this.messageClass = 'alert-danger';
       }
     } catch (error) {
       this.message = 'Failed to fetch campaigns: ' + error.message;
       this.messageClass = 'alert-danger';
     }
   },
   getReachCategory(reach) {
     if (reach < 10000) return 'Low';
     if (reach < 50000) return 'Medium';
     return 'High';
   },

   updateInfluencerDetails() {
     this.selectedInfluencer = this.influencers.find(
       influencer => influencer.id === this.requestForm.influencer_id
     );
   },
   async fetchInfluencers() {
     try {
       const response = await fetch('http://localhost:5000/all_influencers', {
         method: 'GET',
         headers: {
           'Authorization': `Bearer ${localStorage.getItem('access_token')}`
         }
       });
       const data = await response.json();
       if (response.ok) {
         this.influencers = data;
       } else {
         this.message = data.message;
         this.messageClass = 'alert-danger';
       }
     } catch (error) {
       this.message = 'Failed to fetch influencers: ' + error.message;
       this.messageClass = 'alert-danger';
     }
   },
   async fetchRequestsForYou() {
     try {
       const response = await fetch('http://localhost:5000/sponsor/ad-requests', {
         method: 'GET',
         headers: {
           'Authorization': `Bearer ${localStorage.getItem('access_token')}`
         }
       });
       const data = await response.json();
       if (response.ok) {
         this.requestsForYou = data;
       } else {
         this.message = data.message;
         this.messageClass = 'alert-danger';
       }
     } catch (error) {
       this.message = 'Failed to fetch requests: ' + error.message;
       this.messageClass = 'alert-danger';
     }
   },
   openRequestModal(campaignId) {
     this.requestForm.campaign_id = campaignId;
     const requestModal = new bootstrap.Modal(document.getElementById('requestModal'));
     requestModal.show();
   },
   async acceptAdRequest(adRequestId) {
     try {
       const response = await fetch('http://localhost:5000/accept_ad_request', {
         method: 'PUT',
         headers: {
           'Content-Type': 'application/json',
           'Authorization': `Bearer ${localStorage.getItem('access_token')}`
         },
         body: JSON.stringify({ ad_request_id: adRequestId })
       });
       const data = await response.json();
       if (response.ok) {
         this.message = data.message;
         this.messageClass = 'alert-success';
         this.fetchRequestsForYou(); // Refresh the requests
       } else {
         this.message = data.message;
         this.messageClass = 'alert-danger';
       }
     } catch (error) {
       this.message = 'Failed to accept request: ' + error.message;
       this.messageClass = 'alert-danger';
     }
   },
   async rejectAdRequest(adRequestId) {
     try {
       const response = await fetch('http://localhost:5000/reject_ad_request', {
         method: 'PUT',
         headers: {
           'Content-Type': 'application/json',
           'Authorization': `Bearer ${localStorage.getItem('access_token')}`
         },
         body: JSON.stringify({ ad_request_id: adRequestId })
       });
       const data = await response.json();
       if (response.ok) {
         this.message = data.message;
         this.messageClass = 'alert-success';
         this.fetchRequestsForYou(); // Refresh the requests
       } else {
         this.message = data.message;
         this.messageClass = 'alert-danger';
       }
     } catch (error) {
       this.message = 'Failed to reject request: ' + error.message;
       this.messageClass = 'alert-danger';
     }
   },
   async negotiateAdRequest(id) {
     this.$router.push('/negotiation/' + id);
   },
   updateInfluencerDetails() {
     this.selectedInfluencer = this.influencers.find(
       influencer => influencer.id === this.requestForm.influencer_id
     );
   },
   async sendAdRequest() {
     try {
       const response = await fetch('http://localhost:5000/sponsor/send_ad_request', {
         method: 'POST',
         headers: {
           'Content-Type': 'application/json',
           'Authorization': `Bearer ${localStorage.getItem('access_token')}`
         },
         body: JSON.stringify(this.requestForm)
       });
       const data = await response.json();
       if (response.ok) {
         this.message = data.message;
         this.messageClass = 'alert-success';
         const requestModal = bootstrap.Modal.getInstance(document.getElementById('requestModal'));
         requestModal.hide();
       } else {
         this.message = data.message;
         this.messageClass = 'alert-danger';
       }
     } catch (error) {
       this.message = 'Failed to send request: ' + error.message;
       this.messageClass = 'alert-danger';
     }
   },
   editCampaign(campaignId) {
     this.$router.push({ name: 'EditCampaign', params: { campaignId } });
   },
   async deleteCampaign(campaignId) {
     try {
       const response = await fetch(`http://localhost:5000/campaigns/${campaignId}`, {
         method: 'DELETE',
         headers: {
           'Authorization': `Bearer ${localStorage.getItem('access_token')}`
         }
       });
       const data = await response.json();
       if (response.ok) {
         this.campaigns = this.campaigns.filter(campaign => campaign.id !== campaignId);
         this.message = data.message;
         this.messageClass = 'alert-success';
       } else {
         this.message = data.message;
         this.messageClass = 'alert-danger';
       }
     } catch (error) {
       this.message = 'Failed to delete campaign: ' + error.message;
       this.messageClass = 'alert-danger';
     }
   }
 }
};
</script>


<style scoped>
.card {
 box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
 border: none;
}

.card-body {
 text-align: left;
}

.card-title {
 font-size: 1.25rem;
 margin-bottom: 0.75rem;
}

.card-text {
 margin-bottom: 0.75rem;
}


.influencer-details {
 border: 1px solid #ddd;
 padding: 10px;
 margin-bottom: 15px;
 border-radius: 5px;
 background-color: #f8f9fa;
}
</style>
