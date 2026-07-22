import { Routes } from '@angular/router';
import { SubmitPageComponent } from './components/submit-page/submit-page.component';
import { ItemDetailPageComponent } from './components/item-detail-page/item-detail-page.component';
import { AddJiraPageComponent } from './components/add-jira-page/add-jira-page.component';

export const routes: Routes = [
	{
		path: '',
		pathMatch: 'full',
		component: SubmitPageComponent
	},
	{
		path: 'submit',
		redirectTo: ''
	},
	{
		path: 'new-jira',
		component: AddJiraPageComponent
	},
	{
		path: 'items/:id',
		component: ItemDetailPageComponent
	},
	{
		path: '**',
		redirectTo: ''
	}
];
