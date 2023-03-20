<template>
    <tr>
        <th scope="row">{{ index + 1 }}</th>
        <td>{{ item.datetime }}</td>
        <td>{{ item.query_string }}</td>
        <td>
            <div class="d-flex flex-row">
                <div style="font-size: 22px;" v-if="this.item.status.position % 2 != 0">
                    <i class="bi bi-check"></i>
                </div>
                <div v-else class="spinner-border" role="status"></div>
                {{ this.item.status.description }}
            </div>
        </td>
        <td>
            <button class="btn btn-danger" title="Удалить" :disabled="this.item.status.position % 2 == 0"
                @click="deleteHistItem()">
                <i class="bi bi-trash"></i>
            </button>
            <button class="btn btn-primary" title="Открыть результаты" :disabled="this.item.status.position == 0"
                @click="openResults()">
                <i class="bi bi-list-task"></i>
            </button>
            <button v-if="this.item.status.position <= 1" :disabled="this.item.status.position == 0" class="btn btn-primary"
                title="Сформировать архив результатов" @click="makeArchive()">
                <i class="bi bi-file-earmark-zip"></i>
            </button>
            <button v-if="this.item.status.position <= 3 && this.item.status.position >= 2"
                :disabled="this.item.status.position != 3" class="btn btn-primary" title="Скачать архив результатов"
                @click="downloadArchive()">
                <i class="bi bi-cloud-download"></i>
            </button>
        </td>
    </tr>
</template>

<script>
import axios from 'axios';
import emitter from '../emitter.js';
import Swal from 'sweetalert2'

export default {
    data() {
        return {}
    },
    props: ['item', 'index'],
    methods: {
        openResults() {
            this.$router.push(`/results/${this.item.id}`);
        },
        async deleteHistItem() {
            const result = await Swal.fire({
                title: 'Вы уверены, что хотите удалить данные этого запроса?',
                showCancelButton: true,
                confirmButtonText: 'Удалить',
            })
            if (result.isConfirmed) {
                await axios.delete(`/history/${this.item.id}`);
                emitter.emit('deleteHistItem', { id: this.item.id })
                Swal.fire('Данные удалены', '', 'success')
            };
        },
        async makeArchive() {
            await axios.post(`/archives`, { qid: this.item.id });
            await this.updateStatus();
            this.$forceUpdate();
        },
        async downloadArchive() {
            window.open(`/static/archives/${this.item.id}.tgz`);
        },
        async updateStatus() {
            const updatedItem = await axios.get(`/history/${this.item.id}`);
            this.item.status = updatedItem.data.status;
        },
    },
    async mounted() {
        emitter.on('updateStatus', async (data) => {
            if (data.id != this.item.id) {
                return;
            }
            await this.updateStatus();
            this.$forceUpdate();
        });
    }
}
</script>