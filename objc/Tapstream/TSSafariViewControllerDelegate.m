//
//  TSSafariViewControllerDelegate.m
//  ExampleApp
//
//  Created by Adam Bard on 2015-09-12.
//  Copyright © 2015 Example. All rights reserved.
//

#import "TSSafariViewControllerDelegate.h"

#ifdef TS_SAFARI_VIEW_CONTROLLER_ENABLED
#import <SafariServices/SafariServices.h>

@implementation TSSafariViewControllerDelegate


+ (TSSafariViewControllerDelegate*)createWithURLAndCompletion:(NSURL*)url completion:(void (^)(void))completion
{
	TSSafariViewControllerDelegate* me = [[TSSafariViewControllerDelegate alloc] init];

	me.url = url;
	me.completion = completion;
	me.view.hidden = YES;
	me.modalPresentationStyle = UIModalPresentationOverFullScreen;

	return me;
}

- (void)viewDidAppear:(BOOL)animated
{

	SFSafariViewController* safController = [[SFSafariViewController alloc]
											 initWithURL:self.url];
	if(safController != nil){

		[safController setModalPresentationStyle:UIModalPresentationOverFullScreen];
		safController.view.hidden = YES;

		safController.delegate = self;

		//UIViewController* parent = self.parentViewController;
		//[self removeFromParentViewController];


		[self presentViewController:safController animated:NO completion:nil];
	}
	else
	{
		[self dismiss];
	}
}

- (void)dismiss
{
	[self dismissViewControllerAnimated:false completion:self.completion];
}

- (NSArray<UIActivity *> *)safariViewController:(SFSafariViewController *)controller activityItemsForURL:(NSURL *)URL title:(nullable NSString *)title
{
	return nil;
}

- (void)safariViewControllerDidFinish:(SFSafariViewController *)controller
{
}

- (void)safariViewController:(SFSafariViewController *)controller didCompleteInitialLoad:(BOOL)didLoadSuccessfully
{


	[controller dismissViewControllerAnimated:false completion:^{
		[self dismiss];
	}];
}

@end

#else // IOS < 9, define noop implementation

@implementation TSSafariViewControllerDelegate

+ (TSSafariViewControllerDelegate*)createWithURLAndCompletion:(NSURL*)url completion:(void (^)(void))completion
{
	if (completion != nil)
	{
		completion();
	}
	return nil;
}
@end
#endif

