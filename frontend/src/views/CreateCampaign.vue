<template>
    <NavBar />
    <div class="container mt-5">
        <h2>Create Campaign</h2>
        <form @submit.prevent="createCampaign">
            <div class="form-group">
                <label for="name">Campaign Name</label>
                <input type="text" v-model="form.name" class="form-control" required />
            </div>

            <div class="form-group">
                <label for="description">Description</label>
                <textarea v-model="form.description" class="form-control" required></textarea>
            </div>

            <div class="form-group">
                <label for="start_date">Start Date</label>
                <input type="date" v-model="form.start_date" class="form-control" required />
            </div>

            <div class="form-group">
                <label for="end_date">End Date</label>
                <input type="date" v-model="form.end_date" class="form-control" required />
            </div>

            <div class="form-group">
                <label for="budget">Budget</label>
                <input type="number" v-model="form.budget" class="form-control" required />
            </div>

            <div class="form-group">
                <label for="visibility">Visibility</label>
                <select v-model="form.visibility" class="form-control" required>
                    <option value="public">Public</option>
                    <option value="private">Private</option>
                </select>
            </div>

            <div class="form-group">
                <label for="goals">Goals (Enter the reach you want to achieve)</label>
                <textarea v-model="form.goals" class="form-control" required></textarea>
            </div>

            <button type="submit" class="btn btn-primary mt-3">Create Campaign</button>
        </form>
    </div>
</template>

<script>
// import userMixin from '@/mixins/userMixin';
import NavBar from '@/components/NavBar.vue';
export default {
    name: 'CreateCampaign',
    components: { NavBar },
    data() {
        return {
            form: {
                name: '',
                description: '',
                start_date: '',
                end_date: '',
                budget: 0,
                visibility: 'public',
                goals: 0
            }
        };
    },
    methods:{
        async createCampaign() {
            const response = await fetch('http://localhost:5000/campaign', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                },
                body: JSON.stringify(this.form)
            });
            const data = await response.json();
            if (response.ok) {
                alert(data.message);
                this.$router.push('/my-campaigns');
                // Push to My Campaigns page
            } else {
                alert(data.error);
            }
        }
    }

};

</script>